from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger

from app.config import settings
from app.database.engine import init_models
from app.handlers import get_root_router
from app.middlewares.db import DbSessionMiddleware
from app.middlewares.subscription import SubscriptionMiddleware


async def main() -> None:
    logger.info("AniShiroXBot ishga tushmoqda...")

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        storage = RedisStorage.from_url(settings.REDIS_URL)
    except Exception:
        from aiogram.fsm.storage.memory import MemoryStorage

        logger.warning("Redis ulanmadi, MemoryStorage ishlatilmoqda (production uchun tavsiya etilmaydi).")
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    for observer in (dp.message, dp.callback_query):
        observer.middleware(DbSessionMiddleware())
        observer.middleware(SubscriptionMiddleware())

    dp.include_router(get_root_router())

    await init_models()

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Polling boshlandi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
