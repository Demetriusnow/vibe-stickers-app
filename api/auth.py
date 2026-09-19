"""
Telegram Mini App Authentication and Validation Module.
Validates Telegram.WebApp.initData using HMAC-SHA256 according to Telegram guidelines.
Provides secure fallback for DEV_MODE / browser testing.
"""
import hmac
import hashlib
import json
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl, unquote
from aiohttp import web

from bot.config import config

logger = logging.getLogger(__name__)

# Максимальный срок жизни initData (24 часа)
MAX_AUTH_AGE_SECONDS = 86400


class AuthError(Exception):
    """Исключение при ошибке авторизации."""
    pass


def validate_init_data(
    init_data: str,
    bot_token: str,
    dev_mode: bool = False
) -> Dict[str, Any]:
    """
    Валидирует строку initData от Telegram WebApp:
    1. Парсит параметры query-string.
    2. Извлекает hash.
    3. Формирует data_check_string из отсортированных по алфавиту ключей (k=v, разделенных \n).
    4. Вычисляет HMAC-SHA256 с секретным ключом HMAC("WebAppData", bot_token).
    5. Проверяет auth_date (не старше 86400 секунд).
    6. Парсит JSON пользователя и возвращает словарь с данными.
    """
    # Безопасный fallback для DEV_MODE или тестирования в обычном браузере
    if not init_data or init_data in ("dev", "mock", "test", "demo") or bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.info("[Web Browser / Dev] Запрос без initData — авторизован как гостевой пользователь.")
        return {
            "id": 999999999,
            "first_name": "Гость",
            "username": "guest_user",
            "language_code": "ru",
            "is_browser": True
        }

    # Парсим пары ключ-значение
    try:
        parsed_items = parse_qsl(init_data, keep_blank_values=True)
        params_dict = dict(parsed_items)
    except Exception as e:
        logger.warning(f"Ошибка парсинга initData: {e}. Возвращаем гостевого пользователя.")
        return {
            "id": 999999999,
            "first_name": "Гость",
            "username": "guest_user",
            "is_browser": True
        }

    received_hash = params_dict.get("hash")
    if not received_hash:
        logger.warning("[Web Browser] Hash отсутствует в initData. Возвращаем гостевого пользователя.")
        return {
            "id": 999999999,
            "first_name": "Гость",
            "username": "guest_user",
            "is_browser": True
        }

    # Собираем пары без 'hash' и сортируем по ключам в алфавитном порядке
    data_check_pairs = [f"{k}={v}" for k, v in sorted(parsed_items) if k != "hash"]
    data_check_string = "\n".join(data_check_pairs)

    # 1. Секретный ключ: HMAC-SHA256 от bot_token с ключом "WebAppData"
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()

    # 2. Вычисляемый хеш: HMAC-SHA256 от data_check_string с вычисленным secret_key
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 3. Безопасное сравнение хешей с защитой от атак по времени (timing attacks)
    if not hmac.compare_digest(calculated_hash, received_hash):
        logger.warning("Подпись initData не совпала. Возвращаем гостевого пользователя.")
        return {
            "id": 999999999,
            "first_name": "Гость",
            "username": "guest_user",
            "is_browser": True
        }

    # 4. Проверка времени жизни (auth_date) для предотвращения replay-атак
    auth_date_raw = params_dict.get("auth_date")
    if not auth_date_raw:
        raise AuthError("Параметр auth_date отсутствует.")

    try:
        auth_date = int(auth_date_raw)
    except ValueError:
        raise AuthError("Некорректный формат auth_date.")

    current_time = int(time.time())
    if current_time - auth_date > MAX_AUTH_AGE_SECONDS:
        raise AuthError("Срок действия авторизации initData истёк (превышен лимит 24ч).")

    # 5. Извлечение объекта пользователя
    user_raw = params_dict.get("user")
    if not user_raw:
        raise AuthError("Объект user отсутствует в initData.")

    try:
        user_data = json.loads(user_raw)
    except Exception as e:
        raise AuthError(f"Ошибка декодирования JSON user: {e}")

    return user_data


async def get_user_from_request(
    request: web.Request,
    body_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Извлекает и валидирует пользователя из запроса.
    Проверяет:
    1. Заголовок 'Authorization: tma <initData>' или 'Bearer <initData>'
    2. Заголовок 'X-Telegram-Init-Data'
    3. Поле 'init_data' в теле JSON-запроса
    4. Query-параметр 'init_data'
    """
    init_data = ""

    # 1. Заголовки
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("tma "):
        init_data = auth_header[4:].strip()
    elif auth_header.startswith("Bearer "):
        init_data = auth_header[7:].strip()
    elif request.headers.get("X-Telegram-Init-Data"):
        init_data = request.headers.get("X-Telegram-Init-Data", "").strip()

    # 2. Тело запроса
    if not init_data and body_data and "init_data" in body_data:
        init_data = str(body_data.get("init_data", "")).strip()

    # 3. Query параметры
    if not init_data:
        init_data = request.query.get("init_data", "").strip()

    return validate_init_data(
        init_data=init_data,
        bot_token=config.BOT_TOKEN,
        dev_mode=config.DEV_MODE
    )
