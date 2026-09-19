"""
REST API Routes for Telegram Mini App (aiohttp).
Endpoints:
- GET  /api/pack-info      - User sticker pack status & link
- POST /api/generate-vibe  - AI meme vibe punchline generator
- GET  /api/search-gifs    - Video & meme search (Tenor v2 / curated fallback)
- POST /api/commit-sticker - FFmpeg processing & Telegram pack upload
"""
import os
import uuid
import asyncio
import logging
from aiohttp import web
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.config import config
from bot.sticker_manager import (
    get_or_create_sticker_pack,
    get_pack_name,
    get_bot_username
)
from api.auth import get_user_from_request, AuthError
from core.gemini_client import generate_vibe
from core.tenor_client import search_gifs, ai_search_gifs_pipeline
from core.video_processor import process_sticker

logger = logging.getLogger(__name__)

# Семафор для предотвращения перегрузки CPU при параллельной конвертации видео
commit_semaphore = asyncio.Semaphore(3)


async def handle_pack_info(request: web.Request) -> web.Response:
    """
    GET /api/pack-info
    Возвращает актуальный статус персонального стикерпака пользователя.
    """
    try:
        user = await get_user_from_request(request)
    except AuthError as e:
        return web.json_response({"error": str(e)}, status=401)

    bot: Bot = request.app.get("bot")
    user_id = user["id"]

    if not bot or not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        # DEV_MODE заглушка
        return web.json_response({
            "exists": False,
            "pack_name": f"v_{user_id}_by_vibebot",
            "pack_link": f"https://t.me/addstickers/v_{user_id}_by_vibebot",
            "count": 0,
            "title": f"Vibes: {user.get('first_name', 'Dev')}"
        })

    bot_username = await get_bot_username(bot)
    pack_name = get_pack_name(user_id, bot_username)
    pack_link = f"https://t.me/addstickers/{pack_name}"

    try:
        sticker_set = await bot.get_sticker_set(name=pack_name)
        return web.json_response({
            "exists": True,
            "pack_name": pack_name,
            "pack_link": pack_link,
            "count": len(sticker_set.stickers),
            "title": sticker_set.title
        })
    except TelegramBadRequest as e:
        if "STICKERSET_INVALID" in str(e):
            return web.json_response({
                "exists": False,
                "pack_name": pack_name,
                "pack_link": pack_link,
                "count": 0,
                "title": f"Vibes: {user.get('first_name', 'User')}"
            })
        logger.error(f"TelegramBadRequest в /api/pack-info: {e}")
        return web.json_response({"error": "Ошибка проверки стикерпака в Telegram"}, status=500)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка в /api/pack-info: {e}")
        return web.json_response({
            "exists": False,
            "pack_name": pack_name,
            "pack_link": pack_link,
            "count": 0,
            "error": str(e)
        })


async def handle_generate_vibe(request: web.Request) -> web.Response:
    """
    POST /api/generate-vibe
    Генерация сетапа, панчлайна, эмодзи и поискового запроса для мема.
    Тело запроса (JSON): { "category": "it|session|friday|cringe|success|all", "prompt": "..." }
    """
    try:
        body = await request.json() if request.can_read_body else {}
    except Exception:
        body = {}

    category = body.get("category", "all")
    prompt = body.get("prompt", "")

    try:
        result = await generate_vibe(category=category, prompt=prompt)
        return web.json_response({
            "status": "ok",
            "vibe": result
        })
    except Exception as e:
        logger.error(f"Ошибка в handle_generate_vibe: {e}")
        return web.json_response({"error": f"Ошибка генерации вайба: {e}"}, status=500)


async def handle_search_gifs(request: web.Request) -> web.Response:
    """
    GET /api/search-gifs
    Поиск видео/анимаций для мем-фона.
    Query-параметры: ?q=cat&limit=10
    """
    query = request.query.get("q", "")
    limit_str = request.query.get("limit", "10")

    try:
        limit = min(int(limit_str), 30)
    except ValueError:
        limit = 10

    try:
        gifs = await search_gifs(query=query, limit=limit)
        return web.json_response({
            "status": "ok",
            "gifs": gifs
        })
    except Exception as e:
        logger.error(f"Ошибка в handle_search_gifs: {e}")
        return web.json_response({"error": f"Ошибка поиска: {e}"}, status=500)


async def handle_ai_search_gifs(request: web.Request) -> web.Response:
    """
    POST or GET /api/ai-search-gifs
    Интеллектуальный поиск видео/гифок с переводом запроса в теги и авто-панчлайном.
    Принимает JSON (POST) или Query params (GET):
      - query / q: строка запроса на русском или английском
      - limit: количество гифок (по умолчанию 12)
    """
    query = ""
    limit = 12

    if request.method == "POST":
        try:
            body = await request.json() if request.can_read_body else {}
        except Exception:
            body = {}
        query = str(body.get("query") or body.get("q") or "").strip()
        try:
            limit = min(int(body.get("limit", 12)), 30)
        except (ValueError, TypeError):
            limit = 12
    else:
        query = str(request.query.get("q") or request.query.get("query") or "").strip()
        try:
            limit = min(int(request.query.get("limit", 12)), 30)
        except (ValueError, TypeError):
            limit = 12

    try:
        result = await ai_search_gifs_pipeline(query=query, limit=limit)
        return web.json_response({
            "status": "ok",
            **result
        })
    except Exception as e:
        logger.error(f"Ошибка в handle_ai_search_gifs: {e}")
        return web.json_response({"error": f"Ошибка ИИ-поиска гифок: {e}"}, status=500)


async def handle_commit_sticker(request: web.Request) -> web.Response:
    """
    POST /api/commit-sticker
    Сборка видео-стикера (FFmpeg) и загрузка в Telegram Sticker Set.
    Тело запроса (JSON):
    {
        "video_url": "https://...",
        "caption": "ПОНЕЛ ЗРЯ БЫКАСАНУЛ",
        "top_text": "ПОНЕЛ",
        "bottom_text": "ЗРЯ БЫКАСАНУЛ",
        "emoji": "🗿",
        "init_data": "..."
    }
    """
    try:
        body = await request.json()
    except Exception as e:
        return web.json_response({"error": f"Невалидный JSON: {e}"}, status=400)

    # 1. Проверка авторизации
    try:
        user = await get_user_from_request(request, body)
    except AuthError as e:
        return web.json_response({"error": str(e)}, status=401)

    video_url = body.get("video_url")
    if not video_url:
        return web.json_response({"error": "Параметр 'video_url' обязателен."}, status=400)

    caption = body.get("caption", "")
    top_text = body.get("top_text", "")
    bottom_text = body.get("bottom_text", "")
    emoji = body.get("emoji", "🔥")
    font_family = body.get("font_family", "impact")
    text_color = body.get("text_color", "#FFFFFF")
    stroke_color = body.get("stroke_color", "#000000")

    bot: Bot = request.app.get("bot")

    # 2. Конвертация видео с защитой от перегрузки CPU (семафор)
    try:
        async with commit_semaphore:
            logger.info(f"Начало сборки стикера для user_id={user['id']}: '{top_text} / {bottom_text}' (font={font_family}, color={text_color})")
            sticker_bytes = await process_sticker(
                video_url=video_url,
                caption=caption,
                top_text=top_text,
                bottom_text=bottom_text,
                font_family=font_family,
                text_color=text_color,
                stroke_color=stroke_color
            )
    except Exception as e:
        logger.error(f"Ошибка обработки видео в FFmpeg: {e}")
        return web.json_response({"error": f"Ошибка обработки видео: {e}"}, status=500)

    # 3. Добавление в Telegram-стикерпак
    user_id = user["id"]
    user_name = user.get("first_name", "User")
    is_browser = user.get("is_browser", False)

    # Если пользователь тестирует в обычном браузере (вне Telegram WebApp)
    if is_browser or user_id == 999999999 or not bot or not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        webm_filename = f"sticker_{uuid.uuid4().hex[:8]}.webm"
        upload_dir = config.BASE_DIR / "webapp" / "media" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        with open(upload_dir / webm_filename, "wb") as f:
            f.write(sticker_bytes)
        download_url = f"/media/uploads/{webm_filename}"

        logger.info(f"Стикер собран для веб-гостя ({len(sticker_bytes)} байт) -> {download_url}")
        return web.json_response({
            "success": True,
            "is_browser": True,
            "created": True,
            "download_url": download_url,
            "pack_name": f"v_{user_id}_demo",
            "pack_link": f"https://t.me/addstickers/v_{user_id}_demo",
            "message": "Стикер готов! Чтобы сохранить его прямо в Telegram-стикерпак, открой приложение через бота @vibestick_bot."
        })

    try:
        created, pack_name, pack_link = await get_or_create_sticker_pack(
            bot=bot,
            user_id=user_id,
            user_name=user_name,
            sticker_bytes=sticker_bytes,
            emoji=emoji
        )

        return web.json_response({
            "success": True,
            "created": created,
            "pack_name": pack_name,
            "pack_link": pack_link
        })
    except TelegramBadRequest as e:
        err_msg = str(e)
        logger.error(f"TelegramBadRequest при добавлении стикера: {err_msg}")
        err_lower = err_msg.lower()
        if "user not found" in err_lower or "peer_id_invalid" in err_lower:
            return web.json_response({
                "error": "Telegram требует, чтобы ты сначала нажал /start в боте @vibestick_bot! После этого стикерпак создастся моментально.",
                "need_start": True
            }, status=400)
        return web.json_response({"error": f"Ошибка Telegram Bot API: {e}"}, status=400)
    except Exception as e:
        logger.error(f"Ошибка выгрузки стикера: {e}")
        return web.json_response({"error": f"Ошибка выгрузки стикера: {e}"}, status=500)


ALLOWED_MEDIA_EXTENSIONS = {".mp4", ".gif", ".webm", ".mov", ".jpg", ".jpeg", ".png"}
MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


async def handle_upload_media(request: web.Request) -> web.Response:
    """
    POST /api/upload-media
    Загрузка пользовательского видео / GIF / изображения для фона карточки.
    Принимает multipart/form-data с полем 'file'.
    Проверяет размер (до 25 МБ) и расширения (.mp4, .gif, .webm, .mov, .jpg, .jpeg, .png).
    Сохраняет файл с уникальным именем (UUID) в webapp/media/uploads/.
    Возвращает JSON: { "status": "ok", "url": f"/media/uploads/{filename}", "filename": filename }
    """
    try:
        if not request.content_type.startswith("multipart/"):
            return web.json_response({"error": "Content-Type должен быть multipart/form-data"}, status=400)

        reader = await request.multipart()
        field = None

        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == "file":
                field = part
                break

        if not field:
            return web.json_response({"error": "Поле 'file' не найдено в форме"}, status=400)

        original_filename = field.filename or "upload.mp4"
        ext = os.path.splitext(original_filename)[1].lower()

        if ext not in ALLOWED_MEDIA_EXTENSIONS:
            allowed_str = ", ".join(sorted(ALLOWED_MEDIA_EXTENSIONS))
            return web.json_response({
                "error": f"Недопустимый формат файла '{ext}'. Разрешены: {allowed_str}"
            }, status=400)

        safe_filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = config.BASE_DIR / "webapp" / "media" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / safe_filename

        total_size = 0
        with open(file_path, "wb") as f:
            while True:
                chunk = await field.read_chunk(65536)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE_BYTES:
                    f.close()
                    if file_path.exists():
                        file_path.unlink()
                    return web.json_response({
                        "error": "Размер файла превышает допустимый лимит 25 МБ"
                    }, status=413)
                f.write(chunk)

        if total_size == 0:
            if file_path.exists():
                file_path.unlink()
            return web.json_response({"error": "Загруженный файл пуст"}, status=400)

        url = f"/media/uploads/{safe_filename}"
        logger.info(f"Файл успешно сохранён: {file_path} ({total_size} байт) -> {url}")
        return web.json_response({
            "status": "ok",
            "url": url,
            "filename": safe_filename
        })
    except Exception as e:
        logger.error(f"Ошибка в handle_upload_media: {e}")
        return web.json_response({"error": str(e)}, status=500)


def setup_routes(app: web.Application):
    """Регистрирует все маршруты API."""
    app.router.add_get("/api/pack-info", handle_pack_info)
    app.router.add_post("/api/generate-vibe", handle_generate_vibe)
    app.router.add_get("/api/search-gifs", handle_search_gifs)
    app.router.add_post("/api/ai-search-gifs", handle_ai_search_gifs)
    app.router.add_get("/api/ai-search-gifs", handle_ai_search_gifs)
    app.router.add_post("/api/commit-sticker", handle_commit_sticker)
    app.router.add_post("/api/upload-media", handle_upload_media)
