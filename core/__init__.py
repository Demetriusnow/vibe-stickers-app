"""
Core modules for AI Vibe Stickers:
- gemini_client: генерация мемного контента и тегов
- tenor_client: поиск зацикленных видеомемов и кэширование
- video_processor: рендеринг текста (Pillow) и компиляция стикеров WebM VP9 (FFmpeg)
"""

from .gemini_client import generate_vibe, get_fallback_vibe, CATEGORIES, FALLBACK_VIBES
from .tenor_client import search_media, get_fallback_media, FALLBACK_MEDIA_POOL
from .video_processor import (
    process_sticker,
    create_text_overlay_png,
    find_ffmpeg,
    MAX_STICKER_SIZE_BYTES
)

__all__ = [
    "generate_vibe",
    "get_fallback_vibe",
    "CATEGORIES",
    "FALLBACK_VIBES",
    "search_media",
    "get_fallback_media",
    "FALLBACK_MEDIA_POOL",
    "process_sticker",
    "create_text_overlay_png",
    "find_ffmpeg",
    "MAX_STICKER_SIZE_BYTES",
]
