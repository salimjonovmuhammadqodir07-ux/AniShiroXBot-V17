from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.i18n import t


def search_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=t(lang, "search_by_name"), callback_data="search:name"),
            InlineKeyboardButton(text=t(lang, "search_by_code"), callback_data="search:code"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "search_by_genre"), callback_data="search:genre"),
            InlineKeyboardButton(text=t(lang, "search_by_studio"), callback_data="search:studio"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "search_by_rating"), callback_data="search:rating"),
            InlineKeyboardButton(text=t(lang, "search_top"), callback_data="search:top"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "search_popular"), callback_data="search:popular"),
            InlineKeyboardButton(text=t(lang, "search_latest"), callback_data="search:latest"),
        ],
        [InlineKeyboardButton(text=t(lang, "search_all"), callback_data="search:all")],
        [
            InlineKeyboardButton(text=t(lang, "search_movie"), callback_data="search:movie"),
            InlineKeyboardButton(text=t(lang, "search_ova"), callback_data="search:ova"),
            InlineKeyboardButton(text=t(lang, "search_manga"), callback_data="search:manga"),
        ],
        [InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def anime_detail_kb(anime_id: int, episode_count: int, lang: str) -> InlineKeyboardMarkup:
    ep_buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"ep:{anime_id}:{i}")
        for i in range(1, episode_count + 1)
    ]
    # 5 tadan qatorga joylash
    ep_rows = [ep_buttons[i : i + 5] for i in range(0, len(ep_buttons), 5)]
    ep_rows.append(
        [
            InlineKeyboardButton(text=t(lang, "episode_favorite"), callback_data=f"fav:{anime_id}"),
            InlineKeyboardButton(text=t(lang, "episode_share"), switch_inline_query=str(anime_id)),
        ]
    )
    ep_rows.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="menu:search")])
    return InlineKeyboardMarkup(inline_keyboard=ep_rows)


def episode_player_kb(anime_id: int, ep_number: int, total_eps: int, lang: str) -> InlineKeyboardMarkup:
    nav_row = []
    if ep_number > 1:
        nav_row.append(InlineKeyboardButton(text=t(lang, "episode_prev"), callback_data=f"ep:{anime_id}:{ep_number-1}"))
    if ep_number < total_eps:
        nav_row.append(InlineKeyboardButton(text=t(lang, "episode_next"), callback_data=f"ep:{anime_id}:{ep_number+1}"))

    quality_row = [
        InlineKeyboardButton(text=q, callback_data=f"quality:{anime_id}:{ep_number}:{q}")
        for q in ("360p", "480p", "720p", "1080p")
    ]

    rows = [
        [InlineKeyboardButton(text=t(lang, "episode_download"), callback_data=f"dl:{anime_id}:{ep_number}")],
        quality_row,
        nav_row,
        [
            InlineKeyboardButton(text=t(lang, "episode_favorite"), callback_data=f"fav:{anime_id}"),
            InlineKeyboardButton(text=t(lang, "episode_share"), switch_inline_query=str(anime_id)),
        ],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data=f"anime:{anime_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=[r for r in rows if r])
