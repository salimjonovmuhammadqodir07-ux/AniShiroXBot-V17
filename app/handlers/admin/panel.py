from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.admin import admin_panel_kb
from app.utils.filters import IsAdmin

router = Router(name="admin_panel")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
async def open_admin_panel(message: Message) -> None:
    await message.answer("⚙️ <b>Admin Panel</b>", reply_markup=admin_panel_kb())
