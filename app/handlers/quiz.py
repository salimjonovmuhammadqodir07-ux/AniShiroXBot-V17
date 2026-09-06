from __future__ import annotations

import random

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User

router = Router(name="quiz")

QUESTIONS = [
    {
        "q": "Qaysi anime asosiy qahramoni Naruto Uzumaki?",
        "options": ["Naruto", "Bleach", "One Piece", "Death Note"],
        "answer": 0,
    },
    {
        "q": "\"Attack on Titan\" animesida asosiy dushman kim?",
        "options": ["Titanlar", "Robotlar", "Zombilar", "O'lim xudosi"],
        "answer": 0,
    },
    {
        "q": "\"One Piece\"da bosh qahramon qanday xazina qidiradi?",
        "options": ["One Piece", "Dragon Ball", "Sharingan", "Death Note"],
        "answer": 0,
    },
    {
        "q": "Studio Ghibli qaysi mamlakatda joylashgan?",
        "options": ["Yaponiya", "Koreya", "Xitoy", "AQSH"],
        "answer": 0,
    },
]


def _quiz_kb(index: int, options: list[str]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=opt, callback_data=f"quiz:{index}:{i}")] for i, opt in enumerate(options)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(F.text.in_(["🧩 Anime Quiz", "/quiz"]))
async def start_quiz(message: Message) -> None:
    index = random.randrange(len(QUESTIONS))
    question = QUESTIONS[index]
    await message.answer(f"🧩 <b>Anime Quiz</b>\n\n{question['q']}", reply_markup=_quiz_kb(index, question["options"]))


@router.callback_query(F.data.startswith("quiz:"))
async def answer_quiz(callback: CallbackQuery, session: AsyncSession) -> None:
    _, index_str, chosen_str = callback.data.split(":")
    index, chosen = int(index_str), int(chosen_str)
    question = QUESTIONS[index]

    user = await session.get(User, callback.from_user.id)
    if chosen == question["answer"]:
        if user:
            user.coins = (user.coins or 0) + 3
            await session.commit()
        await callback.message.answer(f"✅ To'g'ri javob! +3 coin 🪙 (Jami: {user.coins if user else '-'})")
    else:
        correct = question["options"][question["answer"]]
        await callback.message.answer(f"❌ Noto'g'ri. To'g'ri javob: <b>{correct}</b>")
    await callback.answer()
