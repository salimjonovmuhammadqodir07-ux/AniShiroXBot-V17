from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import PaymentRequest, User
from app.keyboards.admin import payment_review_kb
from app.keyboards.premium import METHODS, PLANS, methods_kb, plans_kb
from app.states.user_states import PremiumStates
from app.utils.i18n import t

router = Router(name="premium")

CARD_BY_METHOD = {
    "click": lambda: settings.PAYMENT_CARD_CLICK,
    "payme": lambda: settings.PAYMENT_CARD_PAYME,
    "uzcard": lambda: settings.PAYMENT_CARD_UZCARD,
    "humo": lambda: settings.PAYMENT_CARD_HUMO,
}


@router.message(F.text.in_(["💎 Premium"]))
async def open_premium(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    await message.answer(t(lang, "premium_title"), reply_markup=plans_kb())


@router.callback_query(F.data.startswith("premium_plan:"))
async def choose_method(callback: CallbackQuery, state: FSMContext) -> None:
    plan = callback.data.split(":")[1]
    await state.update_data(plan=plan)
    await state.set_state(PremiumStates.choosing_method)
    await callback.message.answer("To'lov usulini tanlang:", reply_markup=methods_kb(plan))
    await callback.answer()


@router.callback_query(F.data.startswith("premium_method:"))
async def ask_receipt(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    _, plan, method = callback.data.split(":")
    card = CARD_BY_METHOD[method]()
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"

    await state.update_data(plan=plan, method=method)
    await state.set_state(PremiumStates.waiting_receipt)

    text = (
        f"💳 <b>{METHODS[method]}</b> orqali to'lov qiling:\n\n"
        f"Karta: <code>{card}</code>\n"
        f"Tarif: {PLANS[plan]['label']}\n\n"
        f"{t(lang, 'premium_pay_instructions')}"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.message(PremiumStates.waiting_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    plan, method = data.get("plan"), data.get("method")
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"

    receipt_file_id = message.photo[-1].file_id
    req = PaymentRequest(user_id=message.from_user.id, plan=plan, method=method, receipt_file_id=receipt_file_id)
    session.add(req)
    await session.commit()
    await session.refresh(req)

    await message.answer(t(lang, "premium_receipt_received"))
    await state.clear()

    caption = (
        f"💎 <b>Yangi Premium so'rov</b>\n\n"
        f"👤 User: <code>{message.from_user.id}</code> (@{message.from_user.username or '-'})\n"
        f"📦 Tarif: {PLANS.get(plan, {}).get('label', plan)}\n"
        f"💳 Usul: {METHODS.get(method, method)}"
    )
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_photo(admin_id, receipt_file_id, caption=caption, reply_markup=payment_review_kb(req.id))
        except Exception:
            continue
