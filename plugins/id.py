

"""Get id of the replied user
Syntax: /id"""

from pyrogram import filters
from pyrogram.enums import ParseMode

from bot import Bot


@Bot.on_message(filters.command(["id", "d"], prefixes=["/", "!", ".", "I", "i"]))
async def universal_id(client, message):
    chat = message.chat
    your_id = message.from_user.id
    reply = message.reply_to_message

    text  = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message.id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    # 1) optional username
    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    # 2) chat id
    text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n" if chat.username \
            else f"**[ᴄʜᴀᴛ ɪᴅ:]** `{chat.id}`\n\n"

    # 3) replied details
    if reply and not getattr(reply, "empty", True):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        if reply.from_user:
            text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

        if reply.forward_from_chat:
            text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, **{reply.forward_from_chat.title}**, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

        if reply.sender_chat:
            text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ ɪs `{reply.sender_chat.id}`\n\n"

        # sticker
        if reply.sticker:
            text += f"**sᴛɪᴄᴋᴇʀ ғɪʟᴇ ɪᴅ:** `{reply.sticker.file_id}`\n"
            text += f"**sᴛɪᴄᴋᴇʀ ᴜɴɪǫᴜᴇ ɪᴅ:** `{reply.sticker.file_unique_id}`\n\n"

        # GIF / animation
        if reply.animation:
            text += f"**ɢɪғ ғɪʟᴇ ɪᴅ:** `{reply.animation.file_id}`\n"
            text += f"**ɢɪғ ᴜɴɪǫᴜᴇ ɪᴅ:** `{reply.animation.file_unique_id}`\n\n"

        # audio / voice
        if reply.audio or reply.voice:
            f_id = (reply.audio or reply.voice).file_id
            text += f"**ᴀᴜᴅɪᴏ ғɪʟᴇ ɪᴅ:** `{f_id}`\n\n"

        # video / video-note
        if reply.video or reply.video_note:
            f_id = (reply.video or reply.video_note).file_id
            text += f"**ᴠɪᴅᴇᴏ ғɪʟᴇ ɪᴅ:** `{f_id}`\n\n"

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )
