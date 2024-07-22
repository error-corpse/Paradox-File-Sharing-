from bot import Bot
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.types import Message
from pyrogram import Client, filters  # Import Client
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from helper_func import get_readable_time
from pyrogram.enums.parse_mode import ParseMode


# MongoDB URI
DB_URI = "mongodb+srv://knight_rider:GODGURU12345@knight.jm59gu9.mongodb.net/?retryWrites=true&w=majority"

mongo_client = AsyncIOMotorClient(DB_URI)
db = mongo_client['paradoXstr']


async def get_ping(bot: Bot) -> float:
    start = time.time()
    await bot.get_me()  # Simple call to measure round-trip time
    end = time.time()
    return round((end - start) * 1000, 2)

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    uptime = get_readable_time(delta.seconds)

    ping = await get_ping(bot)

    db_response_time = await get_db_response_time()

    stats_text = (
        f"Bot Uptime: {uptime}\n"
        f"Ping: {ping} ms\n"
        f"Database Response Time: {db_response_time} ms\n"
    )

    await message.reply(stats_text)

# Function to measure DB response time
async def get_db_response_time() -> float:
    start = time.time()
    # Perform a simple query
    await db.command("ping")
    end = time.time()
    return round((end - start) * 1000, 2)  # DB response time in milliseconds


@Bot.on_message(filters.command('users_list') & filters.user(ADMINS))
async def users_list(bot: Bot, message: Message):
    users = await db['users'].find().to_list(length=None)  # Fetch all users
    if not users:
        await message.reply("No users found.")
        return

    users_text = (
        "┏━━━━━━━━━━━━━━━━━┓\n"
        "ㅤㅤ   ㅤ  [ᴜsᴇʀs ʟɪsᴛ]ㅤㅤㅤㅤㅤ\n"
        "┗━━━━━━━━━━━━━━━━━┛\n\n"
        "╔─────────────╗\n"
    )

    for user in users:
        user_name = user.get('username', 'Unknown')
        user_id = user.get('user_id')
        user_mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'
        users_text += f"» {user_mention}\n"

    users_text += "╚─────────────╝"

    await message.reply(users_text, parse_mode=ParseMode.HTML)

# Function to add user to the database
async def add_user(user_id: int, username: str):
    await db['users'].update_one(
        {'user_id': user_id},
        {'$set': {'username': username}},
        upsert=True
    )

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(bot: Bot, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    await add_user(user_id, username)

    await message.reply("Welcome! You are now using the bot.")

@Bot.on_message(filters.private & filters.incoming)
async def useless(bot: Bot, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)