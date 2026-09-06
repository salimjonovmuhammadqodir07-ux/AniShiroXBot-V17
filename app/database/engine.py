"""Async SQLAlchemy engine va session factory."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    """Ilk ishga tushirishda jadvallarni yaratadi (production'da Alembic tavsiya etiladi)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
