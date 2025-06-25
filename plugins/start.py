# line number 160-169 check for changes - token
from pymongo import MongoClient
import asyncio
import base64
import logging
import os
import random
import re
import string
import time
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

#delete_after = 600

client = MongoClient(DB_URI)  # Replace with your MongoDB URI
db = client[DB_NAME]  # Database name
phdlust = db["phdlust"]  # Collection for users
phdlust_tasks = db["phdlust_tasks"] 
deletions = db[DB_DELETE]  # Collection for scheduled deletions
url_shorteners = db[DB_SHORT]  # Collection for URL shortener configurations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


'''
temp_msg = await message.reply("Please wait...")
'''

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
        """
        if "vip-" in decoded_string:
            if not premium_status:
                sent_message = await message.reply_text(
                    "This VIP content is only accessible to premium (VIP) users! \n\nUpgrade to VIP to access. \nClick here /myplan"
                )
                #asyncio.create_task(schedule_auto_delete(client, sent_message.chat.id, sent_message.id, delay=600))
                return 
        """

        if "vip-" in decoded_string: # and not premium_status:
            normal_link = decoded_string.replace("vip-", "get-")
            phdlust = await encode(normal_link)
            linkb = f"https://t.me/{client.username}?start={phdlust}"

            if await is_premium_user(user_id):
                # Provide direct link for premium users
                short_link = linkb
                caption = "🔰 Yᴏᴜ Aʀᴇ Pʀᴇᴍɪᴜᴍ Uꜱᴇʀ ✅\nCʟɪᴄᴋ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴ Tᴏ Wᴀᴛᴄʜ Dɪʀᴇᴄᴛʟʏ"
                button_text = "Cʟɪᴄᴋ Tᴏ Wᴀᴛᴄʜ"
                po = get_random_image(PRM_PICS)
            else:
                # Generate a shortened link for non-premium users
                shortener_ids = ["myshortener1", "myshortener2", "myshortener3"]
                phdlust_magic = random.choice(shortener_ids)
                
                try:
                    short_link = await get_shortlink(phdlust_magic, linkb)
                except ValueError:
                    await message.reply("Failed to generate a short link. Please try again later.\nContact admin @Professor2547")
                    return

                caption = SHORTCAP  # Use default caption for non-premium users
                button_text = "Short Link"
                po = get_random_image(TOKEN_PICS)

            if not short_link:
                await message.reply("Failed to generate a short link.\ncontact admin @Professor2547 ")
                return

            

            buttons = [
                [InlineKeyboardButton(button_text, url=short_link) , InlineKeyboardButton("Tutorial Video", url=TUT_VID)],
                [InlineKeyboardButton("✨ Premium", callback_data="upi_info")]
            ]

            verification_message = await message.reply_photo(
                photo=po,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                #protect_content=PROTECT_CONTENT,
                quote=True
            )
            return  # End execution for non-premium users

        """
        if is_premium_link and not premium_status:
            sent_message = await message.reply_text("This link is for premium users only! \n\nUpgrade to access. \nClick here /myplan")
            #asyncio.create_task(schedule_auto_delete(client, sent_message.chat.id, sent_message.id, delay=600))
            return
        """

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

        # try:
        #     messages = await get_messages(client, ids)

        #     for msg in messages:
        #         if bool(CUSTOM_CAPTION) & bool(msg.document):
        #             caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
        #         else:
        #             caption = "" if not msg.caption else msg.caption.html
    
        #         if DISABLE_CHANNEL_BUTTON:
        #             reply_markup = msg.reply_markup
        #         else:
        #             reply_markup = None
        #         sent_message = await msg.copy(chat_id=message.from_user.id, protect_content=True, caption=caption, reply_markup=reply_markup)
        #         if AUTO_DELETE == True:
        #             asyncio.create_task(schedule_auto_delete(client, sent_message.chat.id, sent_message.id, delay=DELETE_AFTER))
        #         await sleep(0.5)
                
        #     if GET_AGAIN == True:
        #         get_file_markup = InlineKeyboardMarkup([
        #             [InlineKeyboardButton("GET FILE AGAIN", url=f"https://t.me/{client.username}?start={message.text.split()[1]}")]
        #         ])
        #         await message.reply(GET_INFORM, reply_markup=get_file_markup)
 
        # except Exception as e:
        #     logger.error(f"Error fetching messages: {e}")
        # finally:
        #     await temp_msg.delete()
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

    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Try to get invite links from FORCE_SUB_CHANNELS if available
    join_buttons = []
    links = []
    try:
        # Try to use FORCE_SUB_CHANNELS from config
        for channel in FORCE_SUB_CHANNELS:
            try:
                chat = await client.get_chat(channel)
                # Try to get an existing invite link or create a new one
                invite = None
                if hasattr(client, 'invitelinks') and channel in client.invitelinks:
                    invite = client.invitelinks[channel]
                else:
                    # Try to create a new invite link (requires admin rights)
                    invite_obj = await client.create_chat_invite_link(chat.id, creates_join_request=False)
                    invite = invite_obj.invite_link
                if invite:
                    links.append(invite)
            except Exception as e:
                continue  # Skip channels where invite can't be fetched
    except Exception as e:
        pass
    # Fallback to client.invitelinks if nothing found
    if not links and hasattr(client, 'invitelinks'):
        links = list(client.invitelinks.values())
    if not links:
        await message.reply_text("Bot is not admin in any force subscribe channel or no channels configured. Please contact admin.")
        return
    # Create 2x2 grid of join buttons
    for i in range(0, len(links), 2):
        row = []
        for link in links[i:i+2]:
            row.append(InlineKeyboardButton(text="📍 Jᴏɪɴ Cʜᴀɴɴᴇʟ 📍", url=link))
        join_buttons.append(row)
    # Add Try Again button
    start_arg = message.command[1] if len(message.command) > 1 else ''
    try_again_url = f"https://t.me/{getattr(client, 'username', 'BotUsername')}?start={start_arg}"
    join_buttons.append([
        InlineKeyboardButton(
            text='Try Again',
            url=try_again_url
        )
    ])
    await message.reply_photo(
        photo=get_random_image(FORCE_PICS),
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(join_buttons)
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
'''
# Add /addpr command for admins to add premium subscription
@Bot.on_message(filters.command('addpr') & filters.private)
async def add_premium(client: Client, message: Message):
    if message.from_user.id != ADMINS:
        return await message.reply("You don't have permission to add premium users.")

    try:
        command_parts = message.text.split()
        target_user_id = int(command_parts[1])
        duration_in_days = int(command_parts[2])
        await add_premium_user(target_user_id, duration_in_days)
        await message.reply(f"User {target_user_id} added to premium for {duration_in_days} days.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# Add /removepr command for admins to remove premium subscription
@Bot.on_message(filters.command('removepr') & filters.private)
async def remove_premium(client: Client, message: Message):
    if message.from_user.id != ADMINS:
        return await message.reply("You don't have permission to remove premium users.")

    try:
        command_parts = message.text.split()
        target_user_id = int(command_parts[1])
        await remove_premium_user(target_user_id)
        await message.reply(f"User {target_user_id} removed from premium.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# Add /myplan command for users to check their premium subscription status
@Bot.on_message(filters.command('myplan') & filters.private)
async def my_plan(client: Client, message: Message):
    is_premium, expiry_time = await get_user_subscription(message.from_user.id)
    if is_premium:
        time_left = expiry_time - time.time()
        days_left = int(time_left / 86400)
        await message.reply(f"Your premium subscription is active. Time left: {days_left} days.")
    else:
        await message.reply("You are not a premium user.")

# Add /plans command to show available subscription plans
@Bot.on_message(filters.command('plans') & filters.private)
async def show_plans(client: Client, message: Message):
    plans_text = """
Available Subscription Plans:

1. 7 Days Premium - $5
2. 30 Days Premium - $15
3. 90 Days Premium - $35

Use /upi to make the payment.
"""
    await message.reply(plans_text)

# Add /upi command to provide UPI payment details
@Bot.on_message(filters.command('upi') & filters.private)
async def upi_info(client: Client, message: Message):
    upi_text = """
To subscribe to premium, please make the payment via UPI.

UPI ID: your-upi-id@bank

After payment, contact the bot admin to activate your premium subscription.
"""
    await message.reply(upi_text)
'''
