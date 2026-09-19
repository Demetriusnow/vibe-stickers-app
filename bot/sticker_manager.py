"""
Sticker Manager Module for Telegram Video Stickers (Bot API 7.0+).
Handles sticker set creation, adding stickers, and link generation.
"""
import logging
from typing import Optional, Tuple
from aiogram import Bot
from aiogram.types import InputSticker, BufferedInputFile, StickerSet
from aiogram.enums import StickerFormat
from aiogram.exceptions import TelegramBadRequest
import emoji as emoji_lib

logger = logging.getLogger(__name__)

# Кэш username бота
_cached_bot_username: Optional[str] = None


async def get_bot_username(bot: Bot) -> str:
    """Получает и кэширует username бота."""
    global _cached_bot_username
    if _cached_bot_username is None:
        try:
            bot_info = await bot.get_me()
            _cached_bot_username = bot_info.username or "vibestickers_bot"
        except Exception as e:
            logger.warning(f"Не удалось получить username бота: {e}. Используем fallback.")
            _cached_bot_username = "vibestickers_bot"
    return _cached_bot_username


def sanitize_emoji(emoji_str: Optional[str]) -> str:
    """
    Валидирует эмодзи. Telegram Bot API строго требует реальные символы Unicode-эмодзи.
    Если передан некорректный символ или строка, возвращает дефолтный эмодзи 🔥.
    """
    if not emoji_str:
        return "🔥"
    
    # Извлекаем все валидные эмодзи из строки
    extracted = [char for char in emoji_str if emoji_lib.is_emoji(char)]
    if extracted:
        return extracted[0]
    return "🔥"


def get_pack_name(user_id: int, bot_username: str, version: int = 1) -> str:
    """
    Генерирует уникальное имя стикерпака в соответствии с требованиями Telegram:
    - Только латиница, цифры и _
    - Оканчивается на _by_<bot_username>
    - Длина до 64 символов
    """
    clean_bot = bot_username.lower().replace("@", "")
    prefix = f"v{version}_" if version > 1 else "v_"
    pack_name = f"{prefix}{user_id}_by_{clean_bot}"
    # Обрезаем имя с сохранением суффикса, если превышает 64 символа
    if len(pack_name) > 64:
        suffix = f"_by_{clean_bot}"
        max_prefix_len = 64 - len(suffix)
        pack_name = f"{prefix}{user_id}"[:max_prefix_len] + suffix
    return pack_name


async def get_or_create_sticker_pack(
    bot: Bot,
    user_id: int,
    user_name: str,
    sticker_bytes: bytes,
    emoji: str = "🔥"
) -> Tuple[bool, str, str]:
    """
    Получает существующий стикерпак пользователя или создает новый.
    
    Возвращает кортеж: (created: bool, pack_name: str, pack_link: str)
    """
    bot_username = await get_bot_username(bot)
    pack_name = get_pack_name(user_id, bot_username)
    pack_link = f"https://t.me/addstickers/{pack_name}"
    valid_emoji = sanitize_emoji(emoji)

    input_sticker = InputSticker(
        sticker=BufferedInputFile(sticker_bytes, filename="sticker.webm"),
        format=StickerFormat.VIDEO,
        emoji_list=[valid_emoji]
    )

    # Проверяем, существует ли уже стикерпак
    sticker_set: Optional[StickerSet] = None
    try:
        sticker_set = await bot.get_sticker_set(name=pack_name)
    except TelegramBadRequest as e:
        if "STICKERSET_INVALID" in str(e):
            sticker_set = None
        else:
            logger.error(f"Ошибка проверки стикерпака {pack_name}: {e}")
            raise

    if sticker_set is None:
        # Стикерпака нет — создаем новый
        title = f"Vibes: {user_name}" if user_name else f"Vibes #{user_id}"
        # Лимит на длину title — 64 символа
        title = title[:64]

        logger.info(f"Создание нового стикерпака '{pack_name}' для пользователя {user_id}")
        await bot.create_new_sticker_set(
            user_id=user_id,
            name=pack_name,
            title=title,
            stickers=[input_sticker],
            sticker_format=StickerFormat.VIDEO
        )
        return True, pack_name, pack_link
    else:
        # Стикерпак уже существует — добавляем стикер
        logger.info(f"Добавление стикера в существующий пак '{pack_name}' для {user_id}")
        await bot.add_sticker_to_set(
            user_id=user_id,
            name=pack_name,
            sticker=input_sticker
        )
        return False, pack_name, pack_link


async def add_sticker_to_pack(
    bot: Bot,
    user_id: int,
    sticker_bytes: bytes,
    emoji: str = "🔥",
    user_name: str = "User"
) -> str:
    """
    Добавляет стикер в пак пользователя. Если пак не создан — создаёт его.
    Возвращает прямую ссылку на стикерпак.
    """
    _, _, pack_link = await get_or_create_sticker_pack(
        bot=bot,
        user_id=user_id,
        user_name=user_name,
        sticker_bytes=sticker_bytes,
        emoji=emoji
    )
    return pack_link
