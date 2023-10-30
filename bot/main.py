import os
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv


load_dotenv()

# Ініціалізація бота
bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))
dp = Dispatcher(bot)

