import os
from datetime import datetime
import json
from typing import Union

from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.formatting import Bold, Text
from aiogram import types, Router, F

from keyboards import zodiac_keyboard, builder
from FSM import ZodiacStates
from bot_init import bot
from database.messages.db_control import get_message_ids, save_message, add_or_update_user_zodiac, get_horoscope
from misc import ZODIAC_SIGNS

rt = Router()


# Стартовый роутер
@rt.message(CommandStart())
async def start(msg: types.Message, state: FSMContext):
    content = Text(f"Привет ", Bold(msg.from_user.full_name), "!\nВыбери свой знак зодиака")
    sent_mes = await msg.answer(**content.as_kwargs(), reply_markup=zodiac_keyboard)
    save_message(chat_id=msg.chat.id, message_id=sent_mes.message_id)
    await bot.delete_message(msg.chat.id, msg.message_id)
    await state.set_state(ZodiacStates.set_zodiac)


# Ловим только в нужном стейте
@rt.callback_query(F.data("update"))
@rt.message(F.text.in_(ZODIAC_SIGNS))
async def set_zodiac(
        event: Union[types.Message, types.CallbackQuery],
        state: Union[ZodiacStates.set_zodiac, ZodiacStates.chosen_zodiac],
        cursor="0"):
    if isinstance(event, types.Message):
        msg = event
        zod = msg.text[3:]
        add_or_update_user_zodiac(msg.chat.id, zod.lower())
        await state.set_state(ZodiacStates.chosen_zodiac)
        sent_mes = await msg.answer(f"Вы выбрали {msg.text}")
        save_message(chat_id=msg.chat.id, message_id=sent_mes.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id)

        horos = json.loads(get_horoscope(zod))[cursor]
        media_path = os.path.join('signs_photo', f'{zod}.png')
        photo = FSInputFile(path=media_path)
        current_date = datetime.now()
        formated_date = current_date.strftime("%d.%m.%Y")
        sent_mes = await bot.send_photo(chat_id=msg.chat.id,
                                        photo=photo,
                                        caption=f"*{formated_date}*\n{horos}", parse_mode="Markdown",
                                        reply_markup=builder.as_markup()
                                        )
        save_message(msg.chat.id, message_id=sent_mes.message_id)


# Свапнуть ЗЗ можно только в состоянии, когда мы уже выбрали ЗЗ.
# Так что просто свапаем стейт, выводим клаву и ловим предыдущим хэндлером
@rt.message(Command("change_zodiac"))
async def change_zodiac(msg: types.Message, state: ZodiacStates.chosen_zodiac):
    sent_mes = await msg.answer("Выберите новый знак зодиака", reply_markup=zodiac_keyboard)
    save_message(chat_id=msg.chat.id, message_id=sent_mes.message_id)
    await state.set_state(ZodiacStates.set_zodiac)
    await bot.delete_message(msg.chat.id, msg.message_id)


# Не очень понятно, зачем эта команда, если гороскоп обновляется и парсится раз в день и берётся из БД. Но ТЗ есть ТЗ.
@rt.message(Command("update"))
async def update(msg: types.Message, state: ZodiacStates.chosen_zodiac):
    # Обратиться к БД c гороскопами, передав ЗЗ, получить прогноз
    # Выдать прогноз
    await bot.delete_message(msg.chat.id, msg.message_id)
    pass


# Чистим историю в определенном состоянии, чтобы не скинуть выбор нового ЗЗ
# придется хранить id сообщений в бд и пройтись по ним deletemessages для удаления,
# bulk получения id сообщений нет. sad(
@rt.message(Command("clear_history"))
async def clear_history(msg: types.Message, state: ZodiacStates.chosen_zodiac):
    await bot.delete_messages(chat_id=msg.chat.id, message_ids=get_message_ids(chat_id=msg.chat.id))
    await bot.delete_message(msg.chat.id, msg.message_id)


# Ловим любой текст и прикидываемся дэбиком
@rt.message(F.text)
async def unknown_command(msg: types.Message, state: FSMContext):
    sent_mes = await msg.answer("Извините, я не понял")
    await bot.delete_message(msg.chat.id, sent_mes.message_id)
    await bot.delete_message(msg.chat.id, msg.message_id)
