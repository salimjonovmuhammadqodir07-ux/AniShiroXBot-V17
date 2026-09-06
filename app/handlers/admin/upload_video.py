from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import Anime, Episode
from app.keyboards.admin import post_preview_kb
from app.services.autopost import build_post_caption, build_post_keyboard
from app.states.admin_states import UploadVideoStates
from app.utils.filters import IsAdmin

router = Router(name="admin_upload_video")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:upload_video")
async def start_upload(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    result = await session.execute(select(Anime).order_by(Anime.created_at.desc()).limit(15))
    animes = result.scalars().all()
    if not animes:
        await callback.message.answer("Avval anime qo'shing (🎬 Anime qo'shish).")
        await callback.answer()
        return

    lines = "\n".join(f"<code>{a.code}</code> — {a.title}" for a in animes)
    await state.set_state(UploadVideoStates.choose_anime)
    await callback.message.answer(f"Anime kodini kiriting:\n\n{lines}")
    await callback.answer()


@router.message(UploadVideoStates.choose_anime)
async def choose_anime(message: Message, state: FSMContext, session: AsyncSession) -> None:
    result = await session.execute(select(Anime).where(Anime.code == message.text.strip().upper()))
    anime = result.scalar_one_or_none()
    if not anime:
        await message.answer("Bunday kodli anime topilmadi, qaytadan kiriting:")
        return
    await state.update_data(anime_id=anime.id)
    await state.set_state(UploadVideoStates.episode_number)
    await message.answer("📺 Qism raqamini kiriting:")


@router.message(UploadVideoStates.episode_number)
async def set_episode_number(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("Raqam kiriting:")
        return
    await state.update_data(episode_number=int(message.text))
    await state.set_state(UploadVideoStates.video_720)
    await message.answer("🎥 Videoni yuboring (720p sifatida saqlanadi — asosiy fayl):")


@router.message(UploadVideoStates.video_720, F.video)
async def receive_video(message: Message, state: FSMContext) -> None:
    await state.update_data(video_720=message.video.file_id)
    await state.set_state(UploadVideoStates.preview)
    await message.answer(
        "✅ Video qabul qilindi.\n\nQo'shimcha sifatlar (360p/480p/1080p) kerak bo'lsa, "
        "keyinroq admin panel orqali qo'shishingiz mumkin. Hozircha post preview tayyorlanmoqda…"
    )
    await _show_preview(message, state)


async def _show_preview(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(
        f"📝 <b>Post Preview</b>\n\nAnime ID: {data['anime_id']}\nQism: {data['episode_number']}\n\n"
        f"Tasdiqlash uchun quyidagi tugmani bosing.",
        reply_markup=post_preview_kb(data["anime_id"], data["episode_number"]),
    )


@router.callback_query(F.data.startswith("admin:publish:"))
async def publish_post(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    _, _, anime_id_str, ep_number_str = callback.data.split(":")
    anime_id, ep_number = int(anime_id_str), int(ep_number_str)
    data = await state.get_data()

    anime = await session.get(Anime, anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    existing_result = await session.execute(
        select(Episode).where(Episode.anime_id == anime_id, Episode.number == ep_number)
    )
    episode = existing_result.scalar_one_or_none()
    if episode:
        episode.file_id_720 = data.get("video_720") or episode.file_id_720
        episode.file_id_480 = data.get("video_480") or episode.file_id_480
        episode.file_id_360 = data.get("video_360") or episode.file_id_360
        episode.file_id_1080 = data.get("video_1080") or episode.file_id_1080
    else:
        episode = Episode(
            anime_id=anime_id,
            number=ep_number,
            file_id_720=data.get("video_720"),
            file_id_480=data.get("video_480"),
            file_id_360=data.get("video_360"),
            file_id_1080=data.get("video_1080"),
        )
        session.add(episode)
    await session.commit()
    await session.refresh(episode)
    await session.refresh(anime, attribute_names=["episodes"])
    await state.clear()

    bot_info = await callback.bot.get_me()
    caption = build_post_caption(anime, episode)
    kb = build_post_keyboard(bot_info.username, anime.id)

    if settings.MAIN_CHANNEL_ID:
        if anime.poster_file_id:
            await callback.bot.send_photo(settings.MAIN_CHANNEL_ID, anime.poster_file_id, caption=caption, reply_markup=kb)
        else:
            await callback.bot.send_message(settings.MAIN_CHANNEL_ID, caption, reply_markup=kb)
        await callback.message.answer("🚀 Post kanalga muvaffaqiyatli joylandi!")
    else:
        await callback.message.answer("⚠️ MAIN_CHANNEL_ID sozlanmagan — post kanalga joylanmadi.")
    await callback.answer()


@router.callback_query(F.data.startswith("admin:edit_post:"))
async def edit_post(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, anime_id_str, ep_number_str = callback.data.split(":")
    await state.update_data(anime_id=int(anime_id_str), episode_number=int(ep_number_str))
    await state.set_state(UploadVideoStates.video_720)
    await callback.message.answer("🎥 Yangi videoni yuboring (avvalgisi almashtiriladi):")
    await callback.answer()


@router.callback_query(F.data == "admin:cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi.")
    await callback.answer()
