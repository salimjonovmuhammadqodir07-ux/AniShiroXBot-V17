from aiogram import Router

from app.handlers import ai_chat, cabinet, extra, premium, quiz, search, start
from app.handlers.admin import add_anime, panel, tools, upload_video


def get_root_router() -> Router:
    root = Router(name="root")
    root.include_router(panel.router)
    root.include_router(add_anime.router)
    root.include_router(upload_video.router)
    root.include_router(tools.router)

    root.include_router(start.router)
    root.include_router(search.router)
    root.include_router(cabinet.router)
    root.include_router(premium.router)
    root.include_router(ai_chat.router)
    root.include_router(extra.router)
    root.include_router(quiz.router)
    return root
