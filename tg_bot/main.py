import asyncio

from aiogram.dispatcher.dispatcher import Dispatcher
from bot_init import bot
from handlers import rt, scheduler
from database.messages.db import init_db

dp = Dispatcher()


@dp.startup()
async def startup():
    init_db()
    asyncio.create_task(scheduler())


async def main() -> None:
    dp.include_router(rt)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
