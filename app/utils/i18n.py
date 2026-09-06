"""Oddiy JSON-asosli tarjima tizimi (uz / ru / en)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
SUPPORTED_LANGUAGES = ("uz", "ru", "en")


@lru_cache(maxsize=None)
def _load(lang: str) -> dict[str, str]:
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = LOCALES_DIR / "uz.json"
    return json.loads(path.read_text(encoding="utf-8"))


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in SUPPORTED_LANGUAGES else "uz"
    data = _load(lang)
    text = data.get(key) or _load("uz").get(key) or key
    return text.format(**kwargs) if kwargs else text
