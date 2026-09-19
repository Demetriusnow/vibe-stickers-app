"""
Aiohttp Web Application Server setup for Telegram Mini App and REST API.
Serves static assets for webapp and configures routing.
"""
import os
import logging
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher

from bot.config import config
from api.routes import setup_routes

logger = logging.getLogger(__name__)


@web.middleware
async def cors_middleware(request: web.Request, handler):
    """CORS middleware для беспрепятственных запросов из Telegram Webview и браузеров."""
    if request.method == "OPTIONS":
        response = web.Response(status=204)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Telegram-Init-Data"
    return response


async def handle_index(request: web.Request) -> web.FileResponse:
    """Отдаёт главную страницу Mini App (index.html)."""
    webapp_dir = config.BASE_DIR / "webapp"
    index_file = webapp_dir / "index.html"
    if not index_file.exists():
        return web.Response(text="index.html not found", status=404)
    return web.FileResponse(index_file)


async def setup_app(bot: Bot, dp: Dispatcher) -> web.Application:
    """
    Фабрика настройки aiohttp.web.Application:
    - Привязывает инстансы bot и dp к app
    - Регистрирует CORS middleware
    - Настраивает раздачу статики Mini App (/ и /webapp)
    - Подключает REST API маршруты (/api/*)
    """
    app = web.Application(middlewares=[cors_middleware])

    # Сохраняем бот и диспетчер в состоянии приложения
    app["bot"] = bot
    app["dp"] = dp

    # Регистрация API роутов
    setup_routes(app)

    # Путь к папке со статикой Mini App
    webapp_dir = config.BASE_DIR / "webapp"
    if not webapp_dir.exists():
        webapp_dir.mkdir(parents=True, exist_ok=True)

    # Корневой роут и алиасы для Mini App
    app.router.add_get("/", handle_index)
    app.router.add_get("/webapp", handle_index)
    app.router.add_get("/webapp/", handle_index)

    # Прямые роуты для css и js при открытии с корневого пути http://host:port/
    css_dir = webapp_dir / "css"
    if css_dir.exists():
        app.router.add_static("/css", path=css_dir, name="css")

    js_dir = webapp_dir / "js"
    if js_dir.exists():
        app.router.add_static("/js", path=js_dir, name="js")

    media_dir = webapp_dir / "media"
    if not media_dir.exists():
        media_dir.mkdir(parents=True, exist_ok=True)

    uploads_dir = media_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    app.router.add_static("/media/uploads", path=uploads_dir, name="media_uploads")
    app.router.add_static("/media", path=media_dir, name="media")

    # Раздача всей директории webapp по префиксу /webapp
    app.router.add_static("/webapp", path=webapp_dir, name="webapp_static", show_index=True)

    # Хук на закрытие приложения
    async def on_cleanup(app_instance: web.Application):
        logger.info("Закрытие сессий и остановка сервера...")
        if bot and hasattr(bot, "session") and bot.session:
            await bot.session.close()

    app.on_cleanup.append(on_cleanup)

    return app
