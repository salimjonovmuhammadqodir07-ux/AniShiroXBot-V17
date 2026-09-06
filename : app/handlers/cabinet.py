from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Favorite, User, WatchHistory
from app.utils.i18n import t

router = Router(name="cabinet")


@router.message(F.text.in_(["👤 Kabinet", "👤 Кабинет", "👤 Cabinet"]))
async def open_cabinet(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    if not user:
        return
    lang = user.language

    fav_count = (
        await session.execute(select(func.count()).select_from(Favorite).where(Favorite.user_id == user.id))
    ).scalar_one()

    premium_status = "💎 Faol" if user.is_premium else "❌ Faol emas"
    ref_link = f"https://t.me/AniShiroXBot?start=ref{user.id}"

    text = (
        f"{t(lang, 'cabinet_title')}\n\n"
        f"🪪 ID: <code>{user.id}</code>\n"
        f"👤 Ism: {user.full_name}\n"
        f"🌐 Til: {user.language}\n"
        f"💎 Premium: {premium_status}\n"
        f"❤️ Sevimlilar soni: {fav_count}\n"
        f"🪙 Coin: {user.coins}\n"
        f"🔗 Referal havolasi: {ref_link}\n"
        f"👥 Taklif qilinganlar: {user.referral_count}"
    )
    await message.answer(text)


@router.message(F.text.in_(["📜 Tarix", "📜 История", "📜 History"]))
async def show_history(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    result = await session.execute(
        select(WatchHistory).where(WatchHistory.user_id == message.from_user.id).order_by(WatchHistory.updated_at.desc())
    )
    history = result.scalars().all()
    if not history:
        await message.answer(t(lang, "anime_not_found"))
        return
    lines = [f"• Anime ID {h.anime_id} — {h.last_episode}-qismgacha" for h in history[:20]]
    await message.answer("📜 <b>Ko'rish tarixi</b>\n\n" + "\n".join(lines))


@router.message(F.text.in_(["▶️ Davom Etish", "▶️ Продолжить", "▶️ Continue"]))
async def continue_watching(message: Message, session: AsyncSession) -> None:
    result = await session.execute(
        select(WatchHistory).where(WatchHistory.user_id == message.from_user.id).order_by(WatchHistory.updated_at.desc()).limit(1)
    )
    last = result.scalar_one_or_none()
    if not last:
        user = await session.get(User, message.from_user.id)
        await message.answer(t(user.language if user else "uz", "anime_not_found"))
        return
    await message.answer(f"▶️ Anime ID {last.anime_id}, {last.last_episode}-qismdan davom eting.")
