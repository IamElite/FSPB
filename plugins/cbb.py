# https://t.me/Ultroid_Official/524

from pyrogram import __version__, Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from database.database import full_userbase
from bot import Bot
from config import OWNER_ID, ADMINS, CHANNEL, SUPPORT_GROUP, OWNER
from plugins.cmd import *

# Callback query handler
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "about":
        await query.message.edit_text(
            text=f"<b>○ Creator : <a href='tg://user?id={OWNER_ID}'>This Person</a>\n"
                # f"○ Language : <code>Python3</code>\n"
                # f"○ Library : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>\n"
                 f"○ Source Code : <a href='tg://user?id={OWNER_ID}'>Click here</a>\n"
                 f"○ Channel : @{CHANNEL}\n"
                 f"○ Support Group : @{SUPPORT_GROUP}</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔒 Close", callback_data="close")]]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception as e:
            print(f"Error deleting reply-to message: {e}")

    elif data == "upi_info":
        await upi_info(client, query.message)

    elif data == "show_plans":
        await show_plans(client, query.message)

    elif data == "premium_content":
        # Show an alert and then provide the premium content
        await query.answer("Checking Premium Status...", show_alert=True)
        try:
            if await is_premium_user(user_id):
                await query.message.reply_text("You are Premium User ✨! \nEnjoy Direct Ads-Free Access.")
            else:
                await query.message.reply_text("You are not a premium user.\n\nClick Here : /plans \n\nPlease upgrade to access this content.")
        except:
            await query.message.reply_text("Unable To Find out !! \n\nClick here /myplan")
    
    elif data == "shorten_url":
        try:
            shortener_id = "shortener1"  # Replace with the appropriate shortener ID
            original_link = "https://example.com/some-long-url"
            short_link = await get_shortlink(shortener_id, original_link)
            await query.message.reply_text(f"Shortened URL: {short_link}")
        except Exception as e:
            await query.message.reply_text(f"Error: {e}")

# https://t.me/Ultroid_Official/524


# ultroidofficial : YT



