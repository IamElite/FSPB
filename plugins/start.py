# line number 160-169 check for changes - token
from pymongo import MongoClient
import asyncio, base64, logging, os, random, re, string, time, requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import *
from helper_func import *
from database.database import *
from shortzy import Shortzy
from img import FORCE_PICS, START_PICS, TOKEN_PICS, PRM_PICS, get_random_image
from database.utils import start_premium_reminder_scheduler

#delete_after = 600

client = MongoClient(DB_URI)  # Replace with your MongoDB URI
db = client[DB_NAME]  # Database name
phdlust = db["phdlust"]  # Collection for users
phdlust_tasks = db["phdlust_tasks"] 
deletions = db[DB_DELETE]  # Collection for scheduled deletions
url_shorteners = db[DB_SHORT]  # Collection for URL shortener configurations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def shorten_url_clckru(url):
    api_url = f"https://clck.ru/--?url={url}"
    response = requests.get(api_url)
    return response.text

def shorten_url_tinyurl(url):
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    response = requests.get(api_url)
    return response.text

# Add this function to increment and fetch clicks
async def increment_and_get_clicks(link_id):
    result = url_shorteners.find_one_and_update(
        {"_id": link_id},
        {"$inc": {"clicks": 1}},
        return_document=True
    )
    return result.get("clicks", 1) if result else 1

# User ki short limit set karne ka function
async def set_user_short_limit(user_id, limit):
    phdlust.update_one(
        {"user_id": user_id},
        {"$set": {"short_limit": limit}},
        upsert=True
    )

# User ki short limit get karne ka function (default 1)
async def get_user_short_limit(user_id):
    user = phdlust.find_one({"user_id": user_id})
    return user.get("short_limit", 1) if user else 1


#-------------------------------fetch------------------------------

# Fetch URL shortener configuration
async def get_url_shortener_config(shortener_id):
    """Fetch URL shortener configuration from the database."""
    return url_shorteners.find_one({"_id": shortener_id})

# MongoDB Helper Function for listing all shorteners
async def get_all_shorteners():
    """Fetch all URL shortener configurations from the database."""
    return list(url_shorteners.find())  # Convert cursor to a list for easier handling


# Add a new URL shortener configuration
async def add_url_shortener(shortener_id, api_key, base_site):
    """Add a new URL shortener configuration."""
    url_shorteners.insert_one({
        "_id": shortener_id,
        "api_key": api_key,
        "base_site": base_site
    })

# Update an existing URL shortener configuration
async def update_url_shortener(shortener_id, api_key=None, base_site=None):
    """Update an existing URL shortener configuration."""
    update_data = {}
    if api_key:
        update_data["api_key"] = api_key
    if base_site:
        update_data["base_site"] = base_site
    url_shorteners.update_one(
        {"_id": shortener_id},
        {"$set": update_data}
    )

# Remove a URL shortener configuration
async def remove_url_shortener(shortener_id):
    """Remove a URL shortener configuration."""
    url_shorteners.delete_one({"_id": shortener_id})

# List all shortener configurations
async def get_all_shorteners():
    return list(url_shorteners.find())


async def get_shortlink(shortener_id, link):
    """Generate a short link using dynamic configurations."""
    config = await get_url_shortener_config(shortener_id)
    if not config:
        raise ValueError(f"No configuration found for shortener ID: {shortener_id}")
    
    shortzy = Shortzy(api_key=config["api_key"], base_site=config["base_site"])
    short_link = await shortzy.convert(link)
    return short_link

# MongoDB Helper Functions
async def add_premium_user(user_id, duration_in_days):
    expiry_time = time.time() + (duration_in_days * 86400)  # Calculate expiry time in seconds
    phdlust.update_one(
        {"user_id": user_id},
        {"$set": {"is_premium": True, "expiry_time": expiry_time}},
        upsert=True
    )

async def remove_premium_user(user_id):
    phdlust.update_one(
        {"user_id": user_id},
        {"$set": {"is_premium": False, "expiry_time": None}}
    )

async def get_user_subscription(user_id):
    user = phdlust.find_one({"user_id": user_id})
    if user:
        return user.get("is_premium", False), user.get("expiry_time", None)
    return False, None

async def is_premium_user(user_id):
    is_premium, expiry_time = await get_user_subscription(user_id)
    if is_premium and expiry_time > time.time():
        return True
    return False



# Function to add a delete task to the database
async def add_delete_task(chat_id, message_id, delete_at):
    phdlust_tasks.insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "delete_at": delete_at
    })

# Function to delete the notification after a set delay
async def delete_notification(client, chat_id, notification_id, delay):
    await asyncio.sleep(delay)
    try:
        # Delete the notification message
        await client.delete_messages(chat_id=chat_id, message_ids=notification_id)
    except Exception as e:
        print(f"Error deleting notification {notification_id} in chat {chat_id}: {e}")
        
async def schedule_auto_delete(client, chat_id, message_id, delay):
    delete_at = datetime.now() + timedelta(seconds=int(delay))
    await add_delete_task(chat_id, message_id, delete_at)
    
    # Run deletion in the background to prevent blocking
    async def delete_message():
        await asyncio.sleep(int(delay))
        try:
            # Delete the original message
            await client.delete_messages(chat_id=chat_id, message_ids=message_id)
            phdlust_tasks.delete_one({"chat_id": chat_id, "message_id": message_id})  # Remove from DB
            
            # Send a notification about the deletion
            notification_text = DELETE_INFORM
            notification_msg = await client.send_message(chat_id, notification_text)
            
            # Schedule deletion of the notification after 60 seconds
            asyncio.create_task(delete_notification(client, chat_id, notification_msg.id, 40))
        
        except Exception as e:
            print(f"Error deleting message {message_id} in chat {chat_id}: {e}")

    asyncio.create_task(delete_message())  


async def delete_notification_after_delay(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        # Delete the notification message
        await client.delete_messages(chat_id=chat_id, message_ids=message_id)
    except Exception as e:
        print(f"Error deleting notification {message_id} in chat {chat_id}: {e}")


@Client.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message):
    user_id = message.from_user.id

    if not await present_user(user_id):
        try:
            await add_user(user_id)
            logger.info(f"Added new user with ID: {user_id}")
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")

    premium_status = await is_premium_user(user_id)

    if len(message.text) > 7:
        base64_string = message.text.split(" ", 1)[1]
        is_premium_link = False

        try:
            decoded_string = await decode_premium(base64_string)
            is_premium_link = True
        except Exception as e:
            try:
                decoded_string = await decode(base64_string)
            except Exception as e:
                await message.reply_text("Invalid link provided. \n\nGet help /upi")
                return

        if "vip-" in decoded_string: # and not premium_status:
            normal_link = decoded_string.replace("vip-", "get-")
            phdlust = await encode(normal_link)  # <-- yahan variable ka naam badla
            linkb = f"https://t.me/{client.username}?start={phdlust}"
            #linkb = shorten_url_tinyurl(linkb)
        
            if await is_premium_user(user_id):
                # Provide direct link for premium users
                short_link = linkb
                caption = "🔰 Yᴏᴜ Aʀᴇ Pʀᴇᴍɪᴜᴍ Uꜱᴇʀ ✅\nCʟɪᴄᴋ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴ Tᴏ Wᴀᴛᴄʜ Dɪʀᴇᴄᴛʟʏ"
                button_text = "Cʟɪᴄᴋ Tᴏ Wᴀᴛᴄʜ"
        
            else:
                # Non-premium short link generation
                shortener_ids = ["myshortener1", "myshortener2", "myshortener3"]
                phdlust_magic = random.choice(shortener_ids)
        
                try:
                    if message.text.startswith('/st'):
                        args = message.text.split()
                        user_limit = await get_user_short_limit(user_id)
                    
                        if len(args) > 2:
                            linkb = args[1]
                            if not args[2].isdigit() or not 1 <= int(args[2]) <= user_limit:
                                await message.reply(f"Invalid count (1-{min(user_limit,10)})")
                                return
                            count = min(int(args[2]), 10)
                        else:
                            await message.reply("Usage: /st <link> <count>")
                            return
                    
                        await set_user_short_limit(user_id, user_limit - count)
                    
                        for i in range(count):
                            phdlust_magic = random.choice(shortener_ids)
                            short_link = shorten_url_clckru(await get_shortlink(phdlust_magic, linkb))
                            await message.reply(f"{i+1}. {short_link}")
                            await asyncio.sleep(1 if i < 5 else 2)
                        return
                    else:
                        short_link = shorten_url_clckru(await get_shortlink(phdlust_magic, linkb))
        
                except Exception:
                    await message.reply("Short link failed. Contact @DshDm_bot")
                    return
            
            if not premium_status:
                clicks = await increment_and_get_clicks(phdlust_magic)
                caption = SHORTCAP.format(clicks=clicks)
                BUTTON = "∙ ꜱʜσʀᴛ ʟɪηᴋ ∙"
                button_text = BUTTON           
            

        
            buttons = [
                [InlineKeyboardButton(button_text, url=short_link), InlineKeyboardButton("∙ ᴛᴜᴛσʀɪᴧʟ ᴠɪᴅ ∙", url=TUT_VID)],
                [InlineKeyboardButton("∘ ᴘʀєϻɪᴜϻ ∘", callback_data="upi_info")]
            ]
        
            verification_message = await message.reply(
                caption if hasattr(message, 'reply_photo') else caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return  # End execution for non-premium users

        argument = decoded_string.split("-")
        ids = []

        if len(argument) == 3:
            start = int(int(argument[1]) / abs(client.db_channel.id))
            end = int(int(argument[2]) / abs(client.db_channel.id))
            ids = list(range(start, end + 1)) if start <= end else list(range(end, start + 1))
        elif len(argument) == 2:
            ids = [int(int(argument[1]) / abs(client.db_channel.id))]

        temp_msg = await message.reply("Please wait...")
        #asyncio.create_task(schedule_auto_delete(client, temp_msg.chat.id, temp_msg.id, delay=600))

        try:
            messages = await get_messages(client, ids)
        except:
            error_msg = await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        phdlusts = []
        messages = await get_messages(client, ids)
        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None
            
            try:
                messages = await get_messages(client, ids)
                phdlust = await msg.copy(chat_id=message.from_user.id, caption=caption, reply_markup=reply_markup , protect_content=PROTECT_CONTENT)
                phdlusts.append(phdlust)
                if AUTO_DELETE == True:
                    #await message.reply_text(f"The message will be automatically deleted in {delete_after} seconds.")
                    asyncio.create_task(schedule_auto_delete(client, phdlust.chat.id, phdlust.id, delay=DELETE_AFTER))
                await asyncio.sleep(0.2)      
                #asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                phdlust = await msg.copy(chat_id=message.from_user.id, caption=caption, reply_markup=reply_markup , protect_content=PROTECT_CONTENT)
                phdlusts.append(phdlust)     

        # Notify user to get file again if messages are auto-deleted
        if GET_AGAIN == True:
            get_file_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("GET FILE AGAIN", url=f"https://t.me/{client.username}?start={message.text.split()[1]}")]
            ])
            await message.reply(GET_INFORM, reply_markup=get_file_markup)

        if AUTO_DELETE == True:
            delete_notification = await message.reply(NOTIFICATION)
            asyncio.create_task(delete_notification_after_delay(client, delete_notification.chat.id, delete_notification.id, delay=NOTIFICATION_TIME))

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("😊 About Me", callback_data="about"), InlineKeyboardButton("🔒 Close", callback_data="close")],
                [InlineKeyboardButton("✨ Upgrade to Premium" if not premium_status else "✨ Premium Content", callback_data="premium_content")],
            ]
        )
        
        sent_message = await message.reply_photo(
            photo=get_random_image(START_PICS),
            caption=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
            ),
            
            reply_markup=reply_markup,
            #disable_web_page_preview=True, #To of pic -> give #to photo and remove me frome #
            quote=True
        )
        #asyncio.create_task(schedule_auto_delete(client, sent_message.chat.id, sent_message.id, delay=autodelete))
        logger.info(f"Sent welcome message to user {user_id} with premium status: {premium_status}")

    
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id
    buttons, row = [], []

    for i, ch in enumerate(FORCE_SUB_CHANNELS):
        try:
            url = await client.export_chat_invite_link(ch)
            row.append(InlineKeyboardButton(f"📍 Join Fast {i+1} 📍", url=url))
            if len(row) == 2:
                buttons.append(row)
                row = []
        except: pass

    if row: buttons.append(row)

    try_again = []
    if len(message.command) > 1:
        try_again = [InlineKeyboardButton("🔁 Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")]

    if try_again: buttons.append(try_again)

    await message.reply_photo(
        photo=get_random_image(FORCE_PICS),
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=("@" + message.from_user.username) if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )



@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

# At the end of the file or after Bot is initialized, start the scheduler
# (Make sure to pass both bot_instance and phdlust)
import asyncio
from bot import Bot

bot_instance = Bot()

async def on_startup():
    start_premium_reminder_scheduler(bot_instance, phdlust)

asyncio.get_event_loop().create_task(on_startup())
