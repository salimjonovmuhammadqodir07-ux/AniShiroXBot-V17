from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select

from app.config import settings
from app.database.models import RequiredChannel, User
from app.keyboards.main_menu import subscription_kb
from app.utils.i18n import t

# check_sub va admin buyruqlarini bypass qilamiz — cheksiz sikl bo'lmasligi uchun
EXEMPT_CALLBACKS = {"check_sub"}


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        bot = data["bot"]
        session = data.get("session")

        user_id: int | None = None
        lang = "uz"
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            if event.data in EXEMPT_CALLBACKS:
                return await handler(event, data)

        if user_id is None or user_id in settings.admin_ids:
            return await handler(event, data)

        if session is not None:
            user = await session.get(User, user_id)
            if user:
                lang = user.language

            result = await session.execute(select(RequiredChannel))
            channels = result.scalars().all()
        else:
            channels = []

        not_subscribed = []
        for ch in channels:
            try:
                member = await bot.get_chat_member(ch.chat_id, user_id)
                if member.status in ("left", "kicked"):
                    not_subscribed.append(ch)
            except Exception:
                # Kanalga bot admin bo'lmasa yoki xatolik bo'lsa — bloklamaymiz
                continue

        if not_subscribed:
            channel_data = [{"title": c.title or "Kanal", "invite_link": c.invite_link} for c in not_subscribed]
            target = event if isinstance(event, Message) else event.message
            await target.answer(t(lang, "not_subscribed"), reply_markup=subscription_kb(channel_data, lang))
            return None

        return await handler(event, data)
