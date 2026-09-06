from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Anime, BotSetting, User
from app.keyboards.main_menu import language_kb, main_menu_kb
from app.keyboards.search import anime_detail_kb
from app.utils.i18n import t

router = Router(name="start")


async def _get_or_create_user(session: AsyncSession, message: Message, ref_id: int | None = None) -> User:
    user = await session.get(User, message.from_user.id)
    if user is None:
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referred_by=ref_id,
        )
        session.add(user)
        if ref_id and ref_id != message.from_user.id:
            referrer = await session.get(User, ref_id)
            if referrer:
                referrer.referral_count = (referrer.referral_count or 0) + 1
                referrer.coins = (referrer.coins or 0) + 10
        await session.commit()
    return user


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(message: Message, command: CommandObject, session: AsyncSession) -> None:
    payload = command.args or ""

    ref_id = None
    if payload.startswith("ref"):
        try:
            ref_id = int(payload.removeprefix("ref"))
        except ValueError:
            ref_id = None

    user = await _get_or_create_user(session, message, ref_id)

    if payload.startswith("anime"):
        try:
            anime_id = int(payload.removeprefix("anime"))
        except ValueError:
            anime_id = None
        anime = await session.get(Anime, anime_id) if anime_id else None
        if anime:
            caption = (
                f"🎬 <b>{anime.title}</b>\n\n{anime.description or ''}\n\n"
                f"🎭 Janr: {anime.genres or '-'}\n⭐ Reyting: {anime.rating or '-'}"
            )
            kb = anime_detail_kb(anime.id, len(anime.episodes), user.language)
            if anime.poster_file_id:
                await message.answer_photo(anime.poster_file_id, caption=caption, reply_markup=kb)
            else:
                await message.answer(caption, reply_markup=kb)
            return

    await cmd_start(message, session)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    user = await _get_or_create_user(session, message)

    banner = await session.get(BotSetting, "start_banner_file_id")
    welcome_text = await session.get(BotSetting, "start_text")

    text = (welcome_text.value if welcome_text and welcome_text.value else t(user.language, "start_welcome")).format(
        name=message.from_user.full_name
    )

    if banner and banner.value:
        await message.answer_animation(banner.value, caption=text, reply_markup=main_menu_kb(user.language))
    else:
        await message.answer(text, reply_markup=main_menu_kb(user.language))


@router.message(F.text.in_(["🌐 Til Tanlash", "🌐 Язык", "🌐 Language"]))
async def choose_language(message: Message) -> None:
    await message.answer(t("uz", "choose_language"), reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = callback.data.split(":")[1]
    user = await session.get(User, callback.from_user.id)
    if user:
        user.language = lang
        await session.commit()
    await callback.message.answer(t(lang, "subscribed_ok"), reply_markup=main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, session: AsyncSession) -> None:
    # Middleware navbatdagi chaqiruvda qayta tekshiradi; bu yerda foydalanuvchiga signal beramiz
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"
    await callback.message.answer(t(lang, "subscribed_ok"), reply_markup=main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def back_to_main_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_kb(lang))
    await callback.answer()
