import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.storage import Users, Journal, Lessons
from app.scheduler import setup_scheduler
from app.handlers import start, lesson, reflection, daily, stats, settings

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# --- storage ---
users = Users("data/users.json")
journal = Journal("data/journal.json")
lessons = Lessons("data/lessons.json")

# --- inject into handlers via workflow data ---
dp["users"] = users
dp["journal"] = journal
dp["lessons"] = lessons

# --- routers ---
dp.include_router(start.router)
dp.include_router(lesson.router)
dp.include_router(reflection.router)
dp.include_router(daily.router)
dp.include_router(stats.router)
dp.include_router(settings.router)


async def main():
    sched = setup_scheduler(bot, users, lessons)
    try:
        await dp.start_polling(bot)
    finally:
        sched.shutdown()


if __name__ == "__main__":
    print("Stoic Daily Bot — aggel008")
    asyncio.run(main())
