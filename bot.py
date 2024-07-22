from aiohttp import web
from plugins import web_server
import logging
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from datetime import datetime
import sys
import asyncio
from config import API_HASH, API_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT
from pyrogram.errors import BadMsgNotification

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        retries = 5
        while retries > 0:
            try:
                await super().start()
                usr_bot_me = await self.get_me()
                self.uptime = datetime.now()

                try:
                    db_channel = await self.get_chat(CHANNEL_ID)
                    self.db_channel = db_channel
                    test = await self.send_message(chat_id=db_channel.id, text="Test Message")
                    await test.delete()
                except Exception as e:
                    self.LOGGER(__name__).warning(e)
                    self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
                    self.LOGGER(__name__).info("\nBot Stopped")
                    sys.exit()

                self.set_parse_mode(ParseMode.HTML)
                self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/paradoxdump")
                self.LOGGER(__name__).info(f""" \n\n       
 [PARADOX]
                                          """)
                self.username = usr_bot_me.username

                # web-response
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()

                break  # Exit the loop if successful

            except BadMsgNotification as e:
                if e.ID == 16:
                    self.LOGGER(__name__).warning("Client time is out of sync, retrying...")
                    retries -= 1
                    await asyncio.sleep(5)  # Wait before retrying
                else:
                    raise
            except Exception as e:
                self.LOGGER(__name__).error(f"An error occurred: {e}")
                raise

        if retries == 0:
            self.LOGGER(__name__).error("Failed to synchronize client time after several attempts.")
            sys.exit(1)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

# Initialize the bot
bot = Bot()

# Ensure the bot starts
bot.run()