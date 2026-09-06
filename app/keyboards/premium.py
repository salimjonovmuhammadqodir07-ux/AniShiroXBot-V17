from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PLANS = {
    "1_month": {"label": "1 oy — 25,000 so'm", "days": 30},
    "3_month": {"label": "3 oy — 60,000 so'm", "days": 90},
    "12_month": {"label": "12 oy — 200,000 so'm", "days": 365},
}

METHODS = {
    "click": "Click",
    "payme": "Payme",
    "uzcard": "Uzcard",
    "humo": "Humo",
}


def plans_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=v["label"], callback_data=f"premium_plan:{k}")] for k, v in PLANS.items()]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def methods_kb(plan: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"premium_method:{plan}:{key}")]
        for key, label in METHODS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
