# AniShiroXBot

Professional Telegram anime platform bot. Python 3.12, Aiogram 3, PostgreSQL, async SQLAlchemy, Docker.

## Xususiyatlar

- 🔎 Ko'p rejimli anime qidiruv (nom, kod, janr, studio, reyting)
- 👤 Foydalanuvchi kabineti (profil, sevimlilar, tarix, referral, coin)
- 🤖 Ko'p tilli AI suhbat (UZ/RU/EN)
- 💎 Premium tizim (chek asosida to'lov tasdiqlash: Click, Payme, Uzcard, Humo)
- 🔒 Majburiy obuna (kanallarga a'zo bo'lmaguncha bot ishlamaydi)
- ⚙️ To'liq admin panel: anime/video qo'shish, avtomatik post generatsiyasi, broadcast, statistika, backup
- 📅 Anime calendar, ⭐ Top anime, 🎲 Random anime, 🧩 Quiz, 🎁 Daily bonus

## Loyiha strukturasi

```
anishiroxbot/
├── app/
│   ├── main.py                 # Bot entrypoint
│   ├── config.py               # Sozlamalar (pydantic-settings, .env)
│   ├── database/
│   │   ├── engine.py           # Async SQLAlchemy engine/session
│   │   └── models/             # User, Anime, Episode, Favorite, History, Premium, Channel...
│   ├── handlers/                # Foydalanuvchi handlerlari (start, search, cabinet, ai, premium)
│   │   └── admin/                # Admin panel handlerlari
│   ├── keyboards/                # Inline/reply klaviaturalar
│   ├── middlewares/              # Majburiy obuna, throttling, DB session
│   ├── services/                 # Biznes-logika (auto-post generator, AI client, payments)
│   ├── states/                   # FSM holatlar
│   ├── locales/                  # uz.json, ru.json, en.json tarjimalar
│   └── utils/                     # Yordamchi funksiyalar
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── railway.json
├── .env.example
└── alembic/                      # DB migratsiyalari (keyingi bosqichda to'ldiriladi)
```

## O'rnatish (lokal)

```bash
cp .env.example .env   # va qiymatlarni to'ldiring
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Docker bilan ishga tushirish

```bash
docker compose up --build
```

## Render.com'ga deploy

1. Repo'ni GitHub'ga push qiling.
2. Render Dashboard → New → Blueprint → shu repo'ni tanlang (`render.yaml` avtomatik o'qiladi).
3. Environment Variables bo'limida `.env.example` dagi barcha qiymatlarni kiriting.
4. Deploy tugmasini bosing — PostgreSQL va Web Service avtomatik yaratiladi.

## Railway'ga deploy

1. Repo'ni ulang, `railway.json` avtomatik konfiguratsiyani o'qiydi.
2. PostgreSQL plugin qo'shing, `DATABASE_URL` avtomatik beriladi.
3. Environment Variables'ni to'ldiring, Deploy qiling.

## Ishlab chiqilish bosqichlari

- [x] 1. Foundation — struktura, config, DB, Docker
- [x] 2. Core bot — /start, menyu, til, majburiy obuna
- [x] 3. Anime tizimi — qidiruv, anime/video sahifalar
- [x] 4. Admin panel — anime/video qo'shish, post preview/publish
- [x] 5. Auto-post — video yuklash → post generatsiya → kanalga joylash
- [x] 6. Kabinet + premium (chek asosida) + referral/coin
- [x] 7. AI suhbat + yakuniy polish

> **Eslatma:** Click/Payme/Uzcard/Humo uchun bu loyihada **chekni admin qo'lda tasdiqlaydigan** oddiy oqim ishlatilgan (screenshot yuboriladi, admin tasdiqlaydi). Real to'lov gateway integratsiyasi har bir provayder bilan alohida shartnoma, merchant ID va sertifikatlash talab qiladi — buni ulash uchun tegishli hisobga ega bo'lgach `app/services/payments.py` faylini kengaytirish kifoya.
