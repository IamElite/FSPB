# Import required libraries and modules
from bot import Bot
from pyrogram import filters
from config import *
from database.utils import *
from datetime import datetime
from plugins.start import *
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import time

# /help command to show available commands
@Bot.on_message(filters.private & filters.command('help') & filters.user(ADMINS))
async def help_command(bot: Bot, message: Message):
    user_id = message.from_user.id

    if user_id not in ADMINS:
        await message.reply("Only Owner can use this command.")
        return

    help_text = """
📖 <b>Available Commands:</b>

/start - Start the bot and see welcome message.
/help - Show this help message.
/myplan - Check your premium status
/batch - Create link for more than one posts.
/genlink - Create link for one post.
/stats - Check your bot uptime.
/users - View bot statistics (Admins only).
/broadcast - Broadcast any messages to bot users (Admins only).
/addpr id days - Add credits to your account (Admins only).
/removepr id - remove premium user
/getpremiumusers - all premium user d and remaining time
/plans - Show available premium plans.
/upi - Show UPI payment options.

/addshort - adds a new shortener configuration to MongoDB.
/resetshort - displays a list of available shorteners, which can be reset based on user interaction.
/settime or /st - Set shortener limit (Admins only).
"""
    await message.reply(help_text, parse_mode=ParseMode.HTML)


@Bot.on_message(filters.command(["settime", "st"]) & filters.user(ADMINS))
async def set_or_get_short_count(client, message):
    parts = message.text.strip().split()
    user_id = message.from_user.id

    if len(parts) > 1 and parts[1].isdigit():
        count = int(parts[1])
        await set_user_short_limit(user_id, count)
        await message.reply_text(f"✅ Short link count set to {count}x")
    else:
        count = await get_user_short_limit(user_id)
        await message.reply_text(
            f"⚠️ Usage: /settime 1\n\nℹ️ Current active: {count}x"
        )

# ✅ Updated /addpr command to support ID/username/reply
@Bot.on_message(filters.private & filters.command('addpr') & filters.user(ADMINS))
async def add_premium(bot: Bot, message: Message):
    target_user_id = await extract_user(bot, message)
    args = message.text.split()

    if not target_user_id:
        return await message.reply("❌ Invalid user. Use ID, username, or reply to user.")
    if len(args) < 3 or not args[2].isdigit():
        return await message.reply("Usage: /addpr user duration_in_days")

    duration_in_days = int(args[2])
    await add_premium_user(target_user_id, duration_in_days)
    current_date = datetime.now()
    await message.reply(f"✅ User {target_user_id} added to premium for {duration_in_days} days.")
    
    # Log premium user addition to logger group
    await send_log_to_group(
        client=bot,
        user_id=target_user_id,
        admin_user=message.from_user,
        action="Added",
        days=duration_in_days,
        expiry_date=current_date + timedelta(days=duration_in_days)
    )


# ✅ Updated /removepr command to support ID/username/reply
@Bot.on_message(filters.private & filters.command('removepr') & filters.user(ADMINS))
async def remove_premium(bot: Bot, message: Message):
    target_user_id = await extract_user(bot, message)
    if not target_user_id:
        return await message.reply("❌ Invalid user. Use ID, username, or reply to user.")

    # Remove premium from target user
    await remove_premium_user(target_user_id)
    await message.reply(f"✅ User {target_user_id} removed from premium.")

    # Log premium user removal to logger group
    await send_log_to_group(
        bot,
        target_user_id,
        message.from_user,
        "Removed"
    )


async def send_log_to_group(client: Client, user_id: int, admin_user: Message, action: str, days: int = 0, expiry_date: datetime = None):
    action_emoji = "🥳" if action == "Added" else "⚠️"
    header = f"❖ {action_emoji} **#{action}Premium** ❖\n\n"

    user_info = await client.get_users(user_id)
    user_first_name = user_info.first_name
    user_last_name = user_info.last_name if user_info.last_name else ""
    user_name = f"{user_first_name} {user_last_name}" if user_last_name else user_first_name
    user_username = f"@{user_info.username}" if user_info.username else "N/A"
    admin_first_name = admin_user.first_name
    admin_username = admin_user.username if admin_user.username else admin_user.first_name

    current_date = datetime.now()
    formatted_date = current_date.strftime("%d-%m-%Y")
    formatted_time = current_date.strftime("%H:%M:%S")

    log_message = (
        f"{header}"
        f"➜ **ᴀᴄᴛɪᴏɴ:** {action}\n"
        f"➜ **ᴜsᴇʀ_ɪᴅ:** `{user_id}`\n"
        f"➜ **ɴᴀᴍᴇ:** {user_name}\n"
        f"➜ **ᴜsᴇʀɴᴀᴍᴇ:** {user_username}\n\n"
    )

    if action == "Added":
        action_by = f"➜ **ᴀᴅᴅᴇᴅ ʙʏ:** {admin_first_name}\n"
        additional_info = f"➜ **ᴇxᴘɪʀᴇs ᴏɴ:** `{(current_date + timedelta(days=days)).strftime('%d-%m-%Y')}`\n"
    else:
        action_by = f"➜ **ʀᴇᴍᴏᴠᴇᴅ ʙʏ:** {admin_first_name}\n"
        additional_info = ""

    log_message += (
        f"{action_by}"
        f"➜ **ᴅᴀᴛᴇ:** `{formatted_date}`\n"
        f"➜ **ᴛɪᴍᴇ:** `{formatted_time}`\n"
        f"{additional_info}"
    )

    try:
        await client.send_message(LOG_ID, log_message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"Failed to send log message to LOG_ID: {e}")





@Bot.on_message(filters.command('myplan') & filters.private)
async def my_plan(bot: Bot, message: Message):
    is_premium, expiry_time = await get_user_subscription(message.from_user.id)
    
    if is_premium and expiry_time:
        time_left = int(expiry_time - time.time())
        
        if time_left > 0:
            days_left = time_left // 86400
            hours_left = (time_left % 86400) // 3600
            minutes_left = (time_left % 3600) // 60

            response_text = (
                f"✅ Your premium subscription is active.\n\n"
                f"🕒 Time remaining: {days_left} days, {hours_left} hours, {minutes_left} minutes."
            )
            
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Upgrade Plan", callback_data="show_plans")],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                    [InlineKeyboardButton("Contact Support", url=f"https://t.me/{OWNER}")]
                ]
            )
        else:
            # Subscription expired
            response_text = (
                "⚠️ Your premium subscription has expired.\n\n"
                "Renew your subscription to continue enjoying premium features."
                "\nCheck: /plans"
            )
            
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Renew Plan", callback_data="show_plans")],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                    [InlineKeyboardButton("Contact Support", url=f"https://t.me/{OWNER}")]
                ]
            )

    else:
        # User is not a premium member
        response_text = "❌ You are not a premium user.\nView available plans to upgrade.\n\nClick HERE: /plans"
        
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("View Plans", callback_data="show_plans")],
                [InlineKeyboardButton("🔒 Close", callback_data="close")],
                [InlineKeyboardButton("Contact Support", url=f"https://t.me/{OWNER}")]
            ]
        )

    await message.reply_text(response_text, reply_markup=buttons)


# Command to show subscription plans
@Bot.on_message(filters.command('plans') & filters.private)
async def show_plans(bot: Bot, message: Message):
    plans_text = PAYMENT_TEXT 
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Pᴀʏ Vɪᴀ Uᴘɪ", callback_data="upi_info")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")],
        [InlineKeyboardButton("Contact Support", url=f"https://t.me/{OWNER}")]
    ])
    await message.reply(plans_text, reply_markup=buttons, parse_mode=ParseMode.HTML)

# Command to show UPI payment QR code and instructions
@Bot.on_message(filters.command('upi') & filters.private)
async def upi_info(bot: Bot, message: Message):
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=PAYMENT_QR,
        caption=PAYMENT_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Sᴇɴᴅ Sᴄʀᴇᴇɴꜱʜᴏᴛ Hᴇʀᴇ", url=f"https://t.me/{OWNER}")],
                [InlineKeyboardButton("🔒 Close", callback_data="close")]
            ]
        )
    )

# Command to retrieve a list of active premium users (admin only)
@Bot.on_message(filters.private & filters.command('getpremiumusers') & filters.user(ADMINS))
async def get_premium_users(bot: Bot, message: Message):
    try:
        premium_users = phdlust.find({"is_premium": True, "expiry_time": {"$gt": time.time()}})
        if not phdlust.count_documents({"is_premium": True, "expiry_time": {"$gt": time.time()}}):
            return await message.reply("No active premium users found.")

        users_list = [
            f"User ID: {user.get('user_id')} - Premium Expires in {max(int((user.get('expiry_time') - time.time()) / 86400), 0)} days"
            for user in premium_users
        ]
        await message.reply("<b>Premium Users:</b>\n\n" + "\n".join(users_list), parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"Error: {str(e)}")


# Command: /addshort
@Bot.on_message(filters.command("addshort") & filters.user(ADMINS))
async def add_shortener(bot: Bot, message: Message):
    """Handle the /addshort command to add a new shortener."""
    try:
        # Expecting input like: shortener_id|api_key|base_site
        text = message.text.split(" ", 1)
        if len(text) < 2:
            await message.reply_text("Please provide the shortener details in the format: id|api_key|base_site")
            return
        
        shortener_details = text[1]
        if "|" in shortener_details:
            shortener_id, api_key, base_site = shortener_details.split("|")
            await add_url_shortener(shortener_id, api_key, base_site)
            await message.reply_text(f"Shortener `{shortener_id}` added successfully!")
        else:
            await message.reply_text("Invalid format. Please use the format: id|api_key|base_site.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Command: /resetshort
@Bot.on_message(filters.command("resetshort") & filters.user(ADMINS))
async def reset_shortener(bot: Bot, message: Message):
    """Handle the /resetshort command to remove a shortener."""
    try:
        # Expecting the shortener ID as the argument
        text = message.text.split(" ", 1)
        if len(text) < 2:
            await message.reply_text("Please provide the shortener ID to reset.")
            return

        shortener_id = text[1]
        await remove_url_shortener(shortener_id)
        await message.reply_text(f"Shortener `{shortener_id}` has been removed successfully!")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

async def get_all_url_shorteners():
    """Fetch all URL shortener configurations from the database."""
    return url_shorteners.find()  # This retrieves all documents from the "url_shorteners" collection.

# Command: /resetuser
@Bot.on_message(filters.command("resetuser") & filters.user(ADMINS))
async def reset_user(bot: Bot, message: Message):
    """Handle the /resetuser command to remove specific user data."""
    try:
        # Expecting the user ID as the argument
        text = message.text.split(" ", 1)
        if len(text) < 2:
            await message.reply_text("Please provide the user ID to reset.")
            return

        user_id = text[1]
        result = phdlust.delete_one({"user_id": int(user_id)})  # Ensure user_id is treated as an integer
        if result.deleted_count > 0:
            await message.reply_text(f"User data for user ID `{user_id}` has been removed successfully!")
        else:
            await message.reply_text(f"No data found for user ID `{user_id}`.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# MongoDB Helper Function for listing all shorteners
async def get_all_shorteners():
    """Fetch all URL shortener configurations from the database."""
    return list(url_shorteners.find())  # Convert cursor to a list for easier handling



# Command: /viewshorteners
@Bot.on_message(filters.command("viewshorteners") & filters.user(ADMINS))
async def view_shorteners(bot: Bot, message: Message):
    """Handle the /viewshorteners command to list all URL shortener configurations."""
    try:
        shorteners = await get_all_shorteners()
        if not shorteners:
            await message.reply_text("No URL shorteners found in the database.")
            return

        response = "URL Shortener Configurations:\n"
        for shortener in shorteners:
            response += (
                f"ID: `{shortener['_id']}`\n"
                f"API Key: `{shortener['api_key']}`\n"
                f"Base Site: `{shortener['base_site']}`\n\n"
            )

        await message.reply_text(response)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# MongoDB Helper Function for listing all shorteners
async def get_all_shorteners():
    """Fetch all URL shortener configurations from the database."""
    return list(url_shorteners.find())  # Convert cursor to a list for easier handling
