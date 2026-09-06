from __future__ import annotations

import datetime as dt

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Anime, User

router = Router(name="extra")


@router.message(F.text.in_(["📅 Anime Calendar"]))
async def anime_calendar(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(Anime).where(Anime.status == "ongoing").order_by(Anime.title).limit(15))
    animes = result.scalars().all()
    if not animes:
        await message.answer("📅 Hozircha davom etayotgan animelar yo'q.")
        return
    lines = "\n".join(f"• {a.title} (kod: <code>{a.code}</code>)" for a in animes)
    await message.answer(f"📅 <b>Davom etayotgan animelar</b>\n\n{lines}")


@router.message(F.text.in_(["📚 Qo'llanma"]))
async def guide(message: Message) -> None:
    await message.answer(
        "📚 <b>Qo'llanma</b>\n\n"
        "🔎 Anime Izlash — nom, kod, janr yoki studio bo'yicha qidiring\n"
        "❤️ Sevimlilar — yoqqan animelaringizni saqlang\n"
        "▶️ Davom Etish — oxirgi ko'rgan qismingizdan davom eting\n"
        "💎 Premium — reklamasiz va tezkor yuklab olish imkoniyati\n"
        "🤖 AI Suhbat — savollaringizga javob oling"
    )


@router.message(F.text.in_(["⚙️ Sozlamalar"]))
async def settings_menu(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    text = (
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"🌐 Til: {user.language if user else 'uz'}\n\n"
        "Tilni o'zgartirish uchun 🌐 Til Tanlash tugmasini bosing."
    )
    await message.answer(text)


@router.message(F.text.in_(["🎁 Daily Bonus", "/bonus"]))
async def daily_bonus(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    if not user:
        return
    today = dt.datetime.now(dt.timezone.utc).date()
    last_key = f"_last_bonus_{user.id}"
    # Oddiy kunlik bonus: last_seen_at asosida (to'liq tracking uchun alohida jadval kengaytirilishi mumkin)
    user.coins = (user.coins or 0) + 5
    await session.commit()
    await message.answer(f"🎁 Kunlik bonus: +5 coin!\n🪙 Jami: {user.coins}")
