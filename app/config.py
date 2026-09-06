"""Bot sozlamalari — barcha qiymatlar .env fayldan yuklanadi."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_int_list(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Bot
    BOT_TOKEN: str
    ADMIN_IDS: str = ""

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Kanal / majburiy obuna
    MAIN_CHANNEL_ID: int = 0
    MAIN_CHANNEL_USERNAME: str = ""
    REQUIRED_CHANNELS: str = ""

    # AI
    AI_API_KEY: str = ""
    AI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    AI_MODEL: str = "gpt-4o-mini"

    # To'lov kartalari (chek asosida tasdiqlash uchun ko'rsatiladi)
    PAYMENT_CARD_CLICK: str = ""
    PAYMENT_CARD_PAYME: str = ""
    PAYMENT_CARD_UZCARD: str = ""
    PAYMENT_CARD_HUMO: str = ""

    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    DEFAULT_LANGUAGE: str = "uz"

    @property
    def admin_ids(self) -> list[int]:
        return _parse_int_list(self.ADMIN_IDS)

    @property
    def required_channels(self) -> list[int]:
        return _parse_int_list(self.REQUIRED_CHANNELS)


settings = Settings()
