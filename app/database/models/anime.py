from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class Anime(Base):
    __tablename__ = "animes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)  # foydalanuvchi qidiradigan kod
    title: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    genres: Mapped[str | None] = mapped_column(String(256), nullable=True)  # vergul bilan ajratilgan
    studio: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ongoing")  # ongoing / completed
    kind: Mapped[str] = mapped_column(String(16), default="anime")  # anime / film / ova / manga

    poster_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    views: Mapped[int] = mapped_column(Integer, default=0)
    favorites_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="anime", cascade="all, delete-orphan", lazy="selectin", order_by="Episode.number"
    )


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("animes.id", ondelete="CASCADE"))
    number: Mapped[int] = mapped_column(Integer)

    # Har xil sifat uchun alohida file_id (Telegram fayl serverida saqlanadi)
    file_id_360: Mapped[str | None] = mapped_column(String(256), nullable=True)
    file_id_480: Mapped[str | None] = mapped_column(String(256), nullable=True)
    file_id_720: Mapped[str | None] = mapped_column(String(256), nullable=True)
    file_id_1080: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    anime: Mapped["Anime"] = relationship(back_populates="episodes")


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("animes.id", ondelete="CASCADE"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WatchHistory(Base):
    __tablename__ = "watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("animes.id", ondelete="CASCADE"))
    last_episode: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
