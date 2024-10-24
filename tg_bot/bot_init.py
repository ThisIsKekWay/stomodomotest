from aiogram import Bot
from config import settings

bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
