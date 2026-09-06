from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.engine import Base


class PaymentRequest(Base):
    """Foydalanuvchi yuborgan to'lov cheki — admin qo'lda tasdiqlaydi."""

    __tablename__ = "payment_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    plan: Mapped[str] = mapped_column(String(32))  # masalan: "1_month", "3_month"
    method: Mapped[str] = mapped_column(String(16))  # click / payme / uzcard / humo
    receipt_file_id: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending / approved / rejected
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RequiredChannel(Base):
    """Majburiy obuna kanallari ro'yxati (admin panel orqali boshqariladi)."""

    __tablename__ = "required_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    invite_link: Mapped[str | None] = mapped_column(String(256), nullable=True)


class BotSetting(Base):
    """Admin o'zgartira oladigan matn/media (start banner, start matni va h.k.)."""

    __tablename__ = "bot_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str | None] = mapped_column(String(4096), nullable=True)
