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
            text=(
                f"<b>○ Creator : <a href='tg://user?id={OWNER_ID}'>This Person</a>\n"
                f"○ Source Code : <a href='tg://user?id={OWNER_ID}'>Click here</a>\n"
                f"○ Channel : @{CHANNEL}\n"
                f"○ Support Group : @{SUPPORT_GROUP}</b>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    InlineKeyboardButton("🔙 Back", callback_data="back_home"),
                    InlineKeyboardButton("🔒 Close", callback_data="close"),
                ]
            ),
        )

    elif data == "back_home":
        # Re-send the original /start message (or edit the current one if you prefer)
        user_id = query.from_user.id
        premium_status = await is_premium_user(user_id)

        await query.message.edit_caption(
            caption=START_MSG.format(
                first=query.from_user.first_name,
                last=query.from_user.last_name,
                username=None if not query.from_user.username else "@" + query.from_user.username,
                mention=query.from_user.mention,
                id=query.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("😊 About Me", callback_data="about"),
                        InlineKeyboardButton("🔒 Close", callback_data="close"),
                    ],
                    [
                        InlineKeyboardButton(
                            "✨ Upgrade to Premium" if not premium_status else "✨ Premium Content",
                            callback_data="premium_content",
                        )
                    ],
                ]
            ),
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception as e:
            print(f"Error deleting reply-to message: {e}")

    # … rest of your existing elif blocks …

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

