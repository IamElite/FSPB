

from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNELS, CHANNEL_ID, PORT, LOG_ID
import pyrogram.utils

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

name ="""DURGESH"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Handle multiple force subscribe channels
        self.invitelinks = {}
        for channel_id in FORCE_SUB_CHANNELS:
            try:
                link = (await self.get_chat(channel_id)).invite_link
                if not link:
                    await self.export_chat_invite_link(channel_id)
                    link = (await self.get_chat(channel_id)).invite_link
                self.invitelinks[channel_id] = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning(f"Bot can't Export Invite link from Force Sub Channel! Channel ID: {channel_id}")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNELS value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Channel ID: {channel_id}")
                self.LOGGER(__name__).info("\nBot Stopped.")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()

            # Send message to logger group
            try:
                logger_chat = await self.get_chat(LOG_ID)
                startup_msg = await self.send_message(chat_id=logger_chat.id, text="<b>Bot has started!</b>")
                #self.LOGGER(__name__).info("Startup message sent to logger group")
                #await startup_msg.delete()
            except Exception as ex:
                self.LOGGER(__name__).warning(f"Failed to send startup message to logger group: {ex}")

        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!")
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped")
