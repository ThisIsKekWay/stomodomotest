from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from misc import ZODIAC_SIGNS

zodiac_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=sign) for sign in ZODIAC_SIGNS[i:i + 4]] for i in range(0, len(ZODIAC_SIGNS), 4)
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)


def create_update_keyboard(cursor: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Обновить", callback_data=f"{1 - cursor}")

    return builder.as_markup()
