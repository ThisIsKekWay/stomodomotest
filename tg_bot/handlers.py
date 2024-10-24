import os
from datetime import datetime
import json
from typing import Union
import asyncio

from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from aiogram.utils.formatting import Bold, Text
from aiogram import types, Router, F

import aioschedule
from keyboards import zodiac_keyboard, create_update_keyboard
from FSM import ZodiacStates
from bot_init import bot
from database.messages.db_control import (
    get_message_ids, save_message, add_or_update_user_zodiac, get_horoscope, get_user_zodiac, get_last_horo_message,
    update_cursor, get_chat_ids)
from misc import ZODIAC_SIGNS, format_date
from config import settings

rt = Router()


# Стартовый роутер
@rt.message(CommandStart())
async def start(msg: types.Message, state: FSMContext):
    content = Text(f"Привет ", Bold(msg.from_user.full_name), "!\nВыбери свой знак зодиака")
    sent_mes = await msg.answer(**content.as_kwargs(), reply_markup=zodiac_keyboard)
    save_message(chat_id=msg.chat.id,
                 message_id=sent_mes.message_id,
                 message_date=datetime.now().strftime("%d.%m.%Y"),
                 message_type="system",
                 cur=1)
    await bot.delete_message(msg.chat.id, msg.message_id)
    await state.set_state(ZodiacStates.set_zodiac)


# Ловим только в нужном стейте

@rt.message(F.text.in_(ZODIAC_SIGNS))
async def set_zodiac(
        msg: types.Message,
        state: FSMContext):
    zod = msg.text[3:].lower()
    add_or_update_user_zodiac(msg.chat.id, zod)
    await state.set_state(ZodiacStates.chosen_zodiac)
    sent_mes = await msg.answer(f"Вы выбрали {msg.text}")
    save_message(chat_id=msg.chat.id,
                 message_id=sent_mes.message_id,
                 message_date=datetime.now().strftime("%d.%m.%Y"),
                 message_type="system",
                 cur=1)
    await bot.delete_message(msg.chat.id, msg.message_id)

    horos = json.loads(get_horoscope(zod))["0"]
    media_path = os.path.join('signs_photo', f'{zod}.png')
    photo = FSInputFile(path=media_path)
    current_date = datetime.now()
    formated_date = current_date.strftime("%d.%m.%Y")
    sent_mes = await bot.send_photo(chat_id=msg.chat.id,
                                    photo=photo,
                                    caption=f"*{formated_date}*\n{horos}", parse_mode="Markdown",
                                    reply_markup=create_update_keyboard(0)
                                    )
    save_message(msg.chat.id,
                 message_id=sent_mes.message_id,
                 message_date=datetime.now().strftime("%d.%m.%Y"),
                 message_type="horo",
                 cur=1)


# Свапнуть ЗЗ можно только в состоянии, когда мы уже выбрали ЗЗ.
# Так что просто свапаем стейт, выводим клаву и ловим предыдущим хэндлером
@rt.message(Command("change_zodiac"))
async def change_zodiac(msg: types.Message, state: FSMContext):
    sent_mes = await msg.answer("Выберите новый знак зодиака", reply_markup=zodiac_keyboard)
    save_message(chat_id=msg.chat.id,
                 message_id=sent_mes.message_id,
                 message_date=datetime.now().strftime("%d.%m.%Y"),
                 message_type="system",
                 cur=1)
    await state.set_state(ZodiacStates.set_zodiac)
    await bot.delete_message(msg.chat.id, msg.message_id)


# Не очень понятно, зачем эта команда, если гороскоп обновляется и парсится раз в день и берётся из БД. Но ТЗ есть ТЗ.
# Буду парсить два разных гороскопа, не знаю, сколько их надо было
async def update_or_send_message(zod, date, cursor=1):
    formated_date = format_date(datetime.now())
    horo_data = json.loads(get_horoscope(zod))
    horo_text = horo_data[str(cursor)]
    caption = f"*{formated_date}*\n{horo_text}"
    reply_markup = create_update_keyboard(int(cursor))
    return caption, reply_markup


@rt.callback_query(F.data.in_({"0", "1"}))
@rt.message(Command("update"))
async def update(event: Union[types.Message, types.CallbackQuery]):
    if isinstance(event, types.CallbackQuery):
        callback = event
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id
        cursor = int(callback.data)
        date = format_date(callback.message.date)

    if isinstance(event, types.Message):
        msg = get_last_horo_message(event.chat.id)
        message_id, chat_id, _, date, cursor = msg
        await bot.delete_message(event.chat.id, event.message_id)

    zod = get_user_zodiac(chat_id)
    caption, reply_markup = await update_or_send_message(zod, date, int(cursor))
    if cursor == 1:
        update_cursor(chat_id, message_id, 0)
    else:
        update_cursor(chat_id, message_id, 1)

    await bot.edit_message_caption(chat_id=chat_id,
                                   message_id=message_id,
                                   caption=caption,
                                   parse_mode="Markdown",
                                   reply_markup=reply_markup)


# Чистим историю в определенном состоянии, чтобы не скинуть выбор нового ЗЗ
# придется хранить id сообщений в бд и пройтись по ним deletemessages для удаления,
# bulk получения id сообщений нет. sad(
@rt.message(Command("clear_history"))
async def clear_history(msg: types.Message, state: FSMContext):
    ids = get_message_ids(chat_id=msg.chat.id)
    await bot.delete_messages(chat_id=msg.chat.id, message_ids=ids)
    await bot.delete_message(msg.chat.id, msg.message_id)


# Ловим любой текст и прикидываемся дэбиком
@rt.message(F.text)
async def unknown_command(msg: types.Message, state: FSMContext):
    sent_msg = await msg.answer("Извините, я не понял. Удалил ваше сообщение.")
    save_message(chat_id=msg.chat.id,
                 message_id=sent_msg.message_id,
                 message_date=datetime.now().strftime("%d.%m.%Y"),
                 message_type="system",
                 cur=1)
    await bot.delete_message(msg.chat.id, msg.message_id)


async def send_scheduled_msg():
    chat_ids = get_chat_ids()
    for chat_id in chat_ids:
        zod = get_user_zodiac(chat_id)
        date = datetime.now().strftime("%d.%m.%Y")
        media_path = os.path.join('signs_photo', f'{zod}.png')
        photo = FSInputFile(path=media_path)
        caption, reply_markup = await update_or_send_message(zod, date)
        sent_mes = await bot.send_photo(chat_id=chat_id,
                                        photo=photo,
                                        caption=caption, parse_mode="Markdown",
                                        reply_markup=create_update_keyboard(1))
        save_message(chat_id=chat_id,
                     message_id=sent_mes.message_id,
                     message_date=datetime.now().strftime("%d.%m.%Y"),
                     message_type="horo",
                     cur=1)


async def scheduler():
    aioschedule.every().day.at(settings.TIME_FOR_SCHEDULE).do(send_scheduled_msg)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
