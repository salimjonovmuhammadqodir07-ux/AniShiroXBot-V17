from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Anime, Episode, Favorite, User, WatchHistory
from app.keyboards.main_menu import main_menu_kb
from app.keyboards.search import anime_detail_kb, episode_player_kb, search_menu_kb
from app.states.user_states import SearchStates
from app.utils.i18n import t

router = Router(name="search")

QUALITY_FIELD = {
    "360p": "file_id_360",
    "480p": "file_id_480",
    "720p": "file_id_720",
    "1080p": "file_id_1080",
}


async def _user_lang(session: AsyncSession, user_id: int) -> str:
    user = await session.get(User, user_id)
    return user.language if user else "uz"


@router.message(F.text.in_(["🔎 Anime Izlash", "🔎 Поиск аниме", "🔎 Search Anime"]))
async def open_search_menu(message: Message, session: AsyncSession) -> None:
    lang = await _user_lang(session, message.from_user.id)
    await message.answer(t(lang, "menu_search"), reply_markup=search_menu_kb(lang))


@router.callback_query(F.data == "menu:search")
async def open_search_menu_cb(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _user_lang(session, callback.from_user.id)
    await callback.message.answer(t(lang, "menu_search"), reply_markup=search_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("search:"))
async def handle_search_type(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    mode = callback.data.split(":")[1]
    lang = await _user_lang(session, callback.from_user.id)

    if mode in ("name", "code", "genre", "studio"):
        await state.update_data(search_mode=mode)
        await state.set_state(SearchStates.waiting_query)
        await callback.message.answer(t(lang, "enter_query"))
        await callback.answer()
        return

    query = select(Anime)
    if mode == "top":
        query = query.order_by(Anime.rating.desc()).limit(10)
    elif mode == "popular":
        query = query.order_by(Anime.views.desc()).limit(10)
    elif mode == "latest":
        query = query.order_by(Anime.created_at.desc()).limit(10)
    elif mode == "movie":
        query = query.where(Anime.kind == "film")
    elif mode == "ova":
        query = query.where(Anime.kind == "ova")
    elif mode == "manga":
        query = query.where(Anime.kind == "manga")
    elif mode == "all":
        query = query.order_by(Anime.title).limit(30)
    else:
        query = query.limit(10)

    result = await session.execute(query)
    animes = result.scalars().all()
    await _send_results_list(callback.message, animes, lang)
    await callback.answer()


@router.message(SearchStates.waiting_query)
async def process_search_query(message: Message, session: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("search_mode", "name")
    lang = await _user_lang(session, message.from_user.id)
    q = message.text.strip()

    query = select(Anime)
    if mode == "name":
        query = query.where(Anime.title.ilike(f"%{q}%"))
    elif mode == "code":
        query = query.where(Anime.code == q)
    elif mode == "genre":
        query = query.where(Anime.genres.ilike(f"%{q}%"))
    elif mode == "studio":
        query = query.where(Anime.studio.ilike(f"%{q}%"))

    result = await session.execute(query.limit(20))
    animes = result.scalars().all()
    await state.clear()
    await _send_results_list(message, animes, lang)


async def _send_results_list(message: Message, animes: list[Anime], lang: str) -> None:
    if not animes:
        await message.answer(t(lang, "anime_not_found"))
        return
    for anime in animes[:10]:
        await _send_anime_card(message, anime, lang)


async def _send_anime_card(message: Message, anime: Anime, lang: str) -> None:
    caption = (
        f"🎬 <b>{anime.title}</b>\n\n"
        f"{anime.description or ''}\n\n"
        f"🎭 Janr: {anime.genres or '-'}\n"
        f"🏢 Studio: {anime.studio or '-'}\n"
        f"⭐ Reyting: {anime.rating or '-'}\n"
        f"🆔 ID: <code>{anime.code}</code>\n"
        f"📌 Status: {anime.status}\n"
        f"📺 Qismlar: {len(anime.episodes)}"
    )
    kb = anime_detail_kb(anime.id, len(anime.episodes), lang)
    if anime.poster_file_id:
        await message.answer_photo(anime.poster_file_id, caption=caption, reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb)


@router.callback_query(F.data.startswith("anime:"))
async def show_anime_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    anime_id = int(callback.data.split(":")[1])
    lang = await _user_lang(session, callback.from_user.id)
    anime = await session.get(Anime, anime_id)
    if not anime:
        await callback.answer(t(lang, "anime_not_found"), show_alert=True)
        return
    await _send_anime_card(callback.message, anime, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("ep:"))
async def show_episode(callback: CallbackQuery, session: AsyncSession) -> None:
    _, anime_id_str, ep_number_str = callback.data.split(":")
    anime_id, ep_number = int(anime_id_str), int(ep_number_str)
    lang = await _user_lang(session, callback.from_user.id)

    anime = await session.get(Anime, anime_id)
    if not anime:
        await callback.answer(t(lang, "anime_not_found"), show_alert=True)
        return

    episode = next((e for e in anime.episodes if e.number == ep_number), None)
    if not episode:
        await callback.answer(t(lang, "anime_not_found"), show_alert=True)
        return

    anime.views = (anime.views or 0) + 1

    history_result = await session.execute(
        select(WatchHistory).where(WatchHistory.user_id == callback.from_user.id, WatchHistory.anime_id == anime_id)
    )
    history = history_result.scalar_one_or_none()
    if history:
        history.last_episode = ep_number
    else:
        session.add(WatchHistory(user_id=callback.from_user.id, anime_id=anime_id, last_episode=ep_number))
    await session.commit()

    file_id = episode.file_id_720 or episode.file_id_480 or episode.file_id_360 or episode.file_id_1080
    kb = episode_player_kb(anime_id, ep_number, len(anime.episodes), lang)
    caption = f"🎬 {anime.title} — {ep_number}-qism"

    if file_id:
        await callback.message.answer_video(file_id, caption=caption, reply_markup=kb)
    else:
        await callback.message.answer(caption, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"))
async def switch_quality(callback: CallbackQuery, session: AsyncSession) -> None:
    _, anime_id_str, ep_number_str, quality = callback.data.split(":")
    anime_id, ep_number = int(anime_id_str), int(ep_number_str)
    lang = await _user_lang(session, callback.from_user.id)

    anime = await session.get(Anime, anime_id)
    episode = next((e for e in anime.episodes if e.number == ep_number), None) if anime else None
    field = QUALITY_FIELD.get(quality)
    file_id = getattr(episode, field, None) if episode and field else None

    if not file_id:
        await callback.answer("Bu sifatda video mavjud emas.", show_alert=True)
        return

    kb = episode_player_kb(anime_id, ep_number, len(anime.episodes), lang)
    await callback.message.answer_video(file_id, caption=f"🎬 {anime.title} — {ep_number}-qism ({quality})", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("fav:"))
async def add_favorite(callback: CallbackQuery, session: AsyncSession) -> None:
    anime_id = int(callback.data.split(":")[1])
    lang = await _user_lang(session, callback.from_user.id)

    existing = await session.execute(
        select(Favorite).where(Favorite.user_id == callback.from_user.id, Favorite.anime_id == anime_id)
    )
    if existing.scalar_one_or_none():
        await callback.answer(t(lang, "already_in_favorites"), show_alert=True)
        return

    session.add(Favorite(user_id=callback.from_user.id, anime_id=anime_id))
    anime = await session.get(Anime, anime_id)
    if anime:
        anime.favorites_count = (anime.favorites_count or 0) + 1
    await session.commit()
    await callback.answer(t(lang, "added_to_favorites"), show_alert=True)


@router.message(F.text.in_(["⭐ Top Anime"]))
async def top_anime_shortcut(message: Message, session: AsyncSession) -> None:
    lang = await _user_lang(session, message.from_user.id)
    result = await session.execute(select(Anime).order_by(Anime.rating.desc()).limit(10))
    await _send_results_list(message, result.scalars().all(), lang)


@router.message(F.text.in_(["🎲 Random Anime"]))
async def random_anime_shortcut(message: Message, session: AsyncSession) -> None:
    lang = await _user_lang(session, message.from_user.id)
    result = await session.execute(select(Anime).order_by(func.random()).limit(1))
    anime = result.scalar_one_or_none()
    if anime:
        await _send_anime_card(message, anime, lang)
    else:
        await message.answer(t(lang, "anime_not_found"))


@router.message(F.text.in_(["❤️ Sevimlilar"]))
async def favorites_shortcut(message: Message, session: AsyncSession) -> None:
    lang = await _user_lang(session, message.from_user.id)
    result = await session.execute(select(Favorite).where(Favorite.user_id == message.from_user.id))
    favs = result.scalars().all()
    animes = [await session.get(Anime, f.anime_id) for f in favs]
    await _send_results_list(message, [a for a in animes if a], lang)
