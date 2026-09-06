from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Anime, BotSetting, PaymentRequest, RequiredChannel, User
from app.keyboards.premium import PLANS
from app.states.admin_states import BannerStates, BroadcastStates, RequiredChannelStates, StartTextStates
from app.utils.filters import IsAdmin

router = Router(name="admin_tools")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ---------- Statistika ----------
@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    users_count = (await session.execute(select(func.count()).select_from(User))).scalar_one()
    premium_count = (await session.execute(select(func.count()).select_from(User).where(User.is_premium.is_(True)))).scalar_one()
    animes_count = (await session.execute(select(func.count()).select_from(Anime))).scalar_one()
    pending_payments = (
        await session.execute(select(func.count()).select_from(PaymentRequest).where(PaymentRequest.status == "pending"))
    ).scalar_one()

    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {users_count}\n"
        f"💎 Premium foydalanuvchilar: {premium_count}\n"
        f"🎬 Animelar soni: {animes_count}\n"
        f"⏳ Kutilayotgan to'lovlar: {pending_payments}"
    )
    await callback.message.answer(text)
    await callback.answer()


# ---------- Banner ----------
@router.callback_query(F.data == "admin:set_banner")
async def ask_banner(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BannerStates.waiting_media)
    await callback.message.answer("🖼 Yangi banner (video yoki GIF) yuboring:")
    await callback.answer()


@router.message(BannerStates.waiting_media, F.animation | F.video)
async def set_banner(message: Message, state: FSMContext, session: AsyncSession) -> None:
    file_id = message.animation.file_id if message.animation else message.video.file_id
    setting = await session.get(BotSetting, "start_banner_file_id")
    if setting:
        setting.value = file_id
    else:
        session.add(BotSetting(key="start_banner_file_id", value=file_id))
    await session.commit()
    await state.clear()
    await message.answer("✅ Banner yangilandi!")


# ---------- Start matni ----------
@router.callback_query(F.data == "admin:set_start_text")
async def ask_start_text(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(StartTextStates.waiting_text)
    await callback.message.answer("📝 Yangi start matnini yuboring (matn ichida {name} — foydalanuvchi ismi bo'lishi mumkin):")
    await callback.answer()


@router.message(StartTextStates.waiting_text)
async def set_start_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    setting = await session.get(BotSetting, "start_text")
    if setting:
        setting.value = message.text
    else:
        session.add(BotSetting(key="start_text", value=message.text))
    await session.commit()
    await state.clear()
    await message.answer("✅ Start matni yangilandi!")


# ---------- Broadcast ----------
@router.callback_query(F.data == "admin:broadcast")
async def ask_broadcast_content(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BroadcastStates.content)
    await callback.message.answer("📢 Barchaga yuboriladigan xabarni yuboring:")
    await callback.answer()


@router.message(BroadcastStates.content)
async def send_broadcast(message: Message, state: FSMContext, session: AsyncSession) -> None:
    result = await session.execute(select(User.id).where(User.is_banned.is_(False)))
    user_ids = [row[0] for row in result.all()]
    await state.clear()

    sent, failed = 0, 0
    status_msg = await message.answer(f"📤 Yuborilmoqda... 0/{len(user_ids)}")
    for i, uid in enumerate(user_ids, start=1):
        try:
            await message.copy_to(uid)
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 0:
            await status_msg.edit_text(f"📤 Yuborilmoqda... {i}/{len(user_ids)}")
        await asyncio.sleep(0.05)

    await status_msg.edit_text(f"✅ Broadcast tugadi.\n\nYuborildi: {sent}\nXato: {failed}")


# ---------- Premium tasdiqlash ----------
@router.callback_query(F.data == "admin:premium_queue")
async def show_pending_payments(callback: CallbackQuery, session: AsyncSession) -> None:
    result = await session.execute(
        select(PaymentRequest).where(PaymentRequest.status == "pending").order_by(PaymentRequest.created_at)
    )
    pending = result.scalars().all()
    if not pending:
        await callback.message.answer("✅ Kutilayotgan to'lovlar yo'q.")
    else:
        await callback.message.answer(f"⏳ {len(pending)} ta kutilayotgan to'lov bor. Chek yuborilgan xabarlardan tasdiqlang.")
    await callback.answer()


@router.callback_query(F.data.startswith("admin:approve_pay:"))
async def approve_payment(callback: CallbackQuery, session: AsyncSession) -> None:
    import datetime as dt

    request_id = int(callback.data.split(":")[2])
    req = await session.get(PaymentRequest, request_id)
    if not req or req.status != "pending":
        await callback.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    user = await session.get(User, req.user_id)
    days = PLANS.get(req.plan, {}).get("days", 30)
    now = dt.datetime.now(dt.timezone.utc)
    base = user.premium_until if (user.premium_until and user.premium_until > now) else now
    user.is_premium = True
    user.premium_until = base + dt.timedelta(days=days)

    req.status = "approved"
    req.reviewed_by = callback.from_user.id
    req.reviewed_at = now
    await session.commit()

    await callback.bot.send_message(req.user_id, f"🎉 Tabriklaymiz! Premium faollashtirildi ({days} kun).")
    await callback.message.edit_caption(caption=(callback.message.caption or "") + "\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi!")


@router.callback_query(F.data.startswith("admin:reject_pay:"))
async def reject_payment(callback: CallbackQuery, session: AsyncSession) -> None:
    import datetime as dt

    request_id = int(callback.data.split(":")[2])
    req = await session.get(PaymentRequest, request_id)
    if not req or req.status != "pending":
        await callback.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    req.status = "rejected"
    req.reviewed_by = callback.from_user.id
    req.reviewed_at = dt.datetime.now(dt.timezone.utc)
    await session.commit()

    await callback.bot.send_message(req.user_id, "❌ Kechirasiz, to'lovingiz tasdiqlanmadi. Admin bilan bog'laning.")
    await callback.message.edit_caption(caption=(callback.message.caption or "") + "\n\n❌ RAD ETILDI")
    await callback.answer("Rad etildi.")


# ---------- Majburiy obuna kanallari ----------
@router.callback_query(F.data == "admin:required_channels")
async def list_required_channels(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    result = await session.execute(select(RequiredChannel))
    channels = result.scalars().all()
    lines = "\n".join(f"• {c.title or c.chat_id} (<code>{c.chat_id}</code>)" for c in channels) or "Hozircha yo'q."
    await state.set_state(RequiredChannelStates.waiting_channel)
    await callback.message.answer(
        f"🔒 <b>Majburiy obuna kanallari:</b>\n\n{lines}\n\n"
        f"Yangi kanal qo'shish uchun formatda yuboring:\n<code>chat_id|Nomi|https://t.me/invite_link</code>"
    )
    await callback.answer()


@router.message(RequiredChannelStates.waiting_channel)
async def add_required_channel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    try:
        chat_id_str, title, invite_link = message.text.split("|")
        chat_id = int(chat_id_str.strip())
    except ValueError:
        await message.answer("Format xato. Namuna: <code>-1001234567890|Kanal nomi|https://t.me/kanal</code>")
        return

    session.add(RequiredChannel(chat_id=chat_id, title=title.strip(), invite_link=invite_link.strip()))
    await session.commit()
    await state.clear()
    await message.answer("✅ Kanal qo'shildi!")


# ---------- Bot sozlamalari / Backup (joy egallovchi) ----------
@router.callback_query(F.data == "admin:settings")
async def bot_settings(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "⚙️ Bot sozlamalari:\n\n"
        "Bu bo'limda kelajakda: standart til, coin narxlari, referral mukofoti kabi sozlamalar qo'shiladi."
    )
    await callback.answer()


@router.callback_query(F.data == "admin:backup")
async def backup_placeholder(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "💾 Backup/Restore:\n\n"
        "To'liq DB backup uchun hosting muhitida `pg_dump` orqali avtomatik backup skripti sozlanadi "
        "(scripts/backup.sh)."
    )
    await callback.answer()


@router.callback_query(F.data == "admin:channels")
async def channel_management(callback: CallbackQuery) -> None:
    await callback.message.answer("📺 Kanal boshqaruvi — asosiy kanalni .env dagi MAIN_CHANNEL_ID orqali sozlang.")
    await callback.answer()
