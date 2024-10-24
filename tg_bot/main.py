import asyncio

from aiogram.dispatcher.dispatcher import Dispatcher
from bot_init import bot
from handlers import rt
from database.messages.db import init_db
dp = Dispatcher()


async def main() -> None:
    init_db()
    dp.include_router(rt)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
