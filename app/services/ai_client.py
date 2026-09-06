"""OpenAI-compatible chat completion client (AI Suhbat funksiyasi uchun)."""
from __future__ import annotations

import aiohttp

from app.config import settings

SYSTEM_PROMPTS = {
    "uz": "Sen AniShiroX Telegram anime botining do'stona AI yordamchisisan. O'zbek tilida qisqa va foydali javob ber.",
    "ru": "Ты дружелюбный AI-помощник Telegram-бота AniShiroX. Отвечай кратко и полезно на русском языке.",
    "en": "You are the friendly AI assistant of the AniShiroX Telegram bot. Reply briefly and helpfully in English.",
}


async def ask_ai(user_text: str, lang: str = "uz") -> str:
    if not settings.AI_API_KEY:
        return {
            "uz": "🤖 AI hozircha sozlanmagan. Admin API kalitni qo'shishi kerak.",
            "ru": "🤖 AI пока не настроен. Администратор должен добавить API-ключ.",
            "en": "🤖 AI isn't configured yet. The admin needs to add an API key.",
        }.get(lang, "AI not configured.")

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["uz"])},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": 500,
    }
    headers = {"Authorization": f"Bearer {settings.AI_API_KEY}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(settings.AI_API_URL, json=payload, headers=headers, timeout=30) as resp:
            data = await resp.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError):
                return "⚠️ AI javob bera olmadi, birozdan so'ng qayta urinib ko'ring."
