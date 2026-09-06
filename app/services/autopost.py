"""Admin video yuklaganda avtomatik kanal posti (caption + tugmalar) tayyorlaydi."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import Anime, Episode


def build_post_caption(anime: Anime, episode: Episode) -> str:
    return (
        f"🎬 <b>{anime.title}</b>\n"
        f"📺 {episode.number}-qism\n\n"
        f"📝 {anime.description or ''}\n\n"
        f"🎭 Janr: {anime.genres or '-'}\n"
        f"⭐ Reyting: {anime.rating or '-'}\n"
        f"📌 Status: {anime.status}\n\n"
        f"#AniShiroX #{anime.code}"
    )


def build_post_keyboard(bot_username: str, anime_id: int) -> InlineKeyboardMarkup:
    url = f"https://t.me/{bot_username}?start=anime{anime_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="▶️ Ko'rish / Yuklab olish", url=url)]]
    )
