from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_panel_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="🎬 Anime qo'shish", callback_data="admin:add_anime")],
        [InlineKeyboardButton(text="📤 Video yuklash", callback_data="admin:upload_video")],
        [InlineKeyboardButton(text="📝 Post Preview", callback_data="admin:post_preview")],
        [InlineKeyboardButton(text="🖼 Banner almashtirish", callback_data="admin:set_banner")],
        [InlineKeyboardButton(text="📝 Start matnini o'zgartirish", callback_data="admin:set_start_text")],
        [InlineKeyboardButton(text="💎 Premium tasdiqlash", callback_data="admin:premium_queue")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
        [InlineKeyboardButton(text="📺 Kanal boshqaruvi", callback_data="admin:channels")],
        [InlineKeyboardButton(text="🔒 Majburiy obuna", callback_data="admin:required_channels")],
        [InlineKeyboardButton(text="⚙️ Bot sozlamalari", callback_data="admin:settings")],
        [InlineKeyboardButton(text="💾 Backup / Restore", callback_data="admin:backup")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def post_preview_kb(anime_id: int, episode_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"admin:edit_post:{anime_id}:{episode_id}")],
            [InlineKeyboardButton(text="🚀 Post qilish", callback_data=f"admin:publish:{anime_id}:{episode_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:cancel_post")],
        ]
    )


def payment_review_kb(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin:approve_pay:{request_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin:reject_pay:{request_id}"),
            ]
        ]
    )
