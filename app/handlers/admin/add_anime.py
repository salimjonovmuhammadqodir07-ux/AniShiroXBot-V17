from __future__ import annotations

import secrets

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Anime
from app.states.admin_states import AddAnimeStates
from app.utils.filters import IsAdmin

router = Router(name="admin_add_anime")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _gen_code() -> str:
    return secrets.token_hex(3).upper()


@router.callback_query(F.data == "admin:add_anime")
async def start_add_anime(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddAnimeStates.title)
    await callback.message.answer("🎬 Anime nomini kiriting:")
    await callback.answer()


@router.message(AddAnimeStates.title)
async def set_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AddAnimeStates.description)
    await message.answer("📝 Tavsifini kiriting:")


@router.message(AddAnimeStates.description)
async def set_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(AddAnimeStates.genres)
    await message.answer("🎭 Janrlarini kiriting (vergul bilan, masalan: Action, Fantasy):")


@router.message(AddAnimeStates.genres)
async def set_genres(message: Message, state: FSMContext) -> None:
    await state.update_data(genres=message.text)
    await state.set_state(AddAnimeStates.studio)
    await message.answer("🏢 Studiyasini kiriting:")


@router.message(AddAnimeStates.studio)
async def set_studio(message: Message, state: FSMContext) -> None:
    await state.update_data(studio=message.text)
    await state.set_state(AddAnimeStates.rating)
    await message.answer("⭐ Reytingini kiriting (masalan: 8.5):")


@router.message(AddAnimeStates.rating)
async def set_rating(message: Message, state: FSMContext) -> None:
    try:
        rating = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Iltimos, raqam kiriting (masalan: 8.5):")
        return
    await state.update_data(rating=rating)
    await state.set_state(AddAnimeStates.kind)
    await message.answer("📚 Turi: anime / film / ova / manga")


@router.message(AddAnimeStates.kind)
async def set_kind(message: Message, state: FSMContext) -> None:
    kind = message.text.strip().lower()
    if kind not in ("anime", "film", "ova", "manga"):
        await message.answer("Faqat: anime / film / ova / manga")
        return
    await state.update_data(kind=kind)
    await state.set_state(AddAnimeStates.poster)
    await message.answer("🖼 Poster rasmini yuboring:")


@router.message(AddAnimeStates.poster, F.photo)
async def set_poster(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    anime = Anime(
        code=_gen_code(),
        title=data["title"],
        description=data.get("description"),
        genres=data.get("genres"),
        studio=data.get("studio"),
        rating=data.get("rating"),
        kind=data.get("kind", "anime"),
        poster_file_id=message.photo[-1].file_id,
    )
    session.add(anime)
    await session.commit()
    await session.refresh(anime)
    await state.clear()

    await message.answer(
        f"✅ Anime qo'shildi!\n\n🆔 Kod: <code>{anime.code}</code>\n🎬 {anime.title}\n\n"
        f"Endi shu anime uchun video yuklashingiz mumkin: 📤 Video yuklash"
    )
