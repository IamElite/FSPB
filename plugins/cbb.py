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
                "<i>σᴜʀ ʀєᴧʟϻ..</i>\n\n"
                "<blockquote>  <b>● ʟєɢᴧᴄʏ</b><i> <a href='https://t.me/SyntaxRealm'>˹ꜱʏηᴛᴧx-ʀєᴧʟϻ˼</a></i>\n"
                "  <b>● ꜱᴜᴘᴘᴏꝛᴛ ➥</b><i> 4 ᴘʟᴧʏєʀꜱ = ɢᴧϻє σᴠєʀ</i>\n"
                "  <b>● ʙσᴛ ꜰᴧᴛʜєʀ ➥</b><i> <a href='https://t.me/DshDm_bot?start'>˹σꜰꜰɪᴄɪᴧʟ-ᴅᴜʀɢєꜱʜ˼</a></i>\n"
                "  <b>● σᴘᴘσηєηᴛ ➥</b><i>|| ϻє ᴠꜱ ϻє ||</i></blockquote>\n"
                "<b>ησᴛє :-</b>\n"
                "<i>ʏσᴜ ᴄᴧη ᴜꜱє σᴜʀ ᴄσηᴛєηᴛ ꜰσʀ ᴄσϻϻєʀᴄɪᴧʟ ᴘᴜʀᴘσꜱєꜱ, ησ ᴄσᴘʏʀɪɢʜᴛ ᴡɪʟʟ ʙє ʟσꜱᴛ ꜰʀσϻ σᴜʀ ꜱɪᴅє.</i>\n\n"
                "<i>ꜱᴧʏσηᴧʀᴧ!!</i>"
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⇇ ʙᴀᴄᴋ ❈", callback_data="home"),
                        InlineKeyboardButton("〆 ᴄʟᴏsᴇ 〆", callback_data="close"),
                    ]
                ]
            ),
        )

    elif data == "home":
        user_id = query.from_user.id
        premium_status = await is_premium_user(user_id)

        await query.message.edit_text(
            text=START_MSG.format(
                mention=query.from_user.mention,
                botmention=(await client.get_me()).mention,
                first=query.from_user.first_name,
                last=query.from_user.last_name,
                username=None
                if not query.from_user.username
                else '@' + query.from_user.username,
                id=query.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("❖ ᴛᴧᴘ тᴏ sᴇᴇ ᴍᴧɢɪᴄ ʙᴧʙʏ ❖", callback_data="about")],
                    [InlineKeyboardButton("˹ ❍ᴡɴᴇꝛ ˼", url=f"https://t.me/DvisDmBot?start"), InlineKeyboardButton("˹ ❍ᴡɴᴇꝛ 𝟮 ˼", url=f"https://t.me/DvisDmBot?start")],
                    [InlineKeyboardButton("〆 ᴄʟᴏsᴇ 〆", callback_data="close")],
                ]
            ),
            parse_mode=ParseMode.HTML,
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

