from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.services.ai_client import ask_ai
from app.states.user_states import AIChatStates
from app.utils.i18n import t

router = Router(name="ai_chat")


@router.message(F.text.in_(["🤖 AI Suhbat", "🤖 AI Чат", "🤖 AI Chat"]))
async def start_ai_chat(message: Message, session: AsyncSession, state: FSMContext) -> None:
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    await state.set_state(AIChatStates.chatting)
    await message.answer(t(lang, "ai_intro"))


@router.message(AIChatStates.chatting)
async def handle_ai_message(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    reply = await ask_ai(message.text, lang)
    await message.answer(reply)
