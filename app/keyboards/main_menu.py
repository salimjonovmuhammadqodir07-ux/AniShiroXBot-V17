from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.utils.i18n import t


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=t(lang, "menu_search")), KeyboardButton(text=t(lang, "menu_cabinet"))],
        [KeyboardButton(text=t(lang, "menu_ai")), KeyboardButton(text=t(lang, "menu_premium"))],
        [KeyboardButton(text=t(lang, "menu_top")), KeyboardButton(text=t(lang, "menu_random"))],
        [KeyboardButton(text=t(lang, "menu_favorites")), KeyboardButton(text=t(lang, "menu_history"))],
        [KeyboardButton(text=t(lang, "menu_continue")), KeyboardButton(text=t(lang, "menu_calendar"))],
        [KeyboardButton(text=t(lang, "menu_guide")), KeyboardButton(text=t(lang, "menu_settings"))],
        [KeyboardButton(text="🧩 Anime Quiz"), KeyboardButton(text="🎁 Daily Bonus")],
        [KeyboardButton(text=t(lang, "menu_language"))],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def subscription_kb(channels: list[dict], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📢 {c['title']}", url=c["invite_link"])]
        for c in channels
        if c.get("invite_link")
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "check_subscription"), callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
