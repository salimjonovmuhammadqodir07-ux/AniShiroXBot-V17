from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from loguru import logger

from app.config import settings
from app.database.engine import init_models
from app.handlers import get_root_router
from app.middlewares.db import DbSessionMiddleware
from app.middlewares.subscription import SubscriptionMiddleware


async def main() -> None:
    logger.info("AniShiroXBot ishga tushmoqda...")

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    for observer in (dp.message, dp.callback_query):
        observer.middleware(DbSessionMiddleware())
        observer.middleware(SubscriptionMiddleware())

    dp.include_router(get_root_router())

    await init_models()

    async def health(request):
        return web.Response(text="OK")

    web_app = web.Application()
    web_app.router.add_get("/", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    logger.info("Health-check server ishga tushdi.")

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Polling boshlandi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
