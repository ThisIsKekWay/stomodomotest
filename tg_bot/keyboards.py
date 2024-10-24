from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from misc import ZODIAC_SIGNS


zodiac_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=sign) for sign in ZODIAC_SIGNS[i:i + 4]] for i in range(3)
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

builder = InlineKeyboardBuilder()
builder.button(text="Обновить", callback_data="update")
