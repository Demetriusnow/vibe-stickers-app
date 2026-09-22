"""
Tenor GIF/Video Search Client for AI Vibe Stickers.
Поиск зацикленных коротких mp4/tinymp4 видеомемов по тегам.
Включает локальное кэширование поисковых запросов и богатый встроенный пул
из 33+ универсальных культовых видеомемов для мгновенного отклика и оффлайн-работы.
"""

import os
import time
import urllib.parse
import random
import logging
import asyncio
from typing import List, Dict, Any, Optional
import aiohttp

try:
    from bot.config import config
    DEFAULT_TENOR_KEY = config.TENOR_API_KEY
except Exception:
    DEFAULT_TENOR_KEY = os.getenv("TENOR_API_KEY", "")

logger = logging.getLogger(__name__)

# Локальный кэш: query -> (timestamp, list_of_media)
_QUERY_CACHE: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS = 3600  # 1 час

# Каталог проверенных публичных мем-видео (33 культовых ролика) для работы без внешних ключей API
FALLBACK_MEMES: List[Dict[str, Any]] = [
    # 1. Fine Dog
    {
        "id": "fine_dog",
        "title": "This is fine dog",
        "url": "/media/fine_dog.mp4",
        "preview_url": "/media/fine_dog.mp4",
        "tags": ["it", "it_deadline", "fire", "panic", "fine", "dog", "coffee", "chaos", "flames", "deadline", "session", "study_exam", "exam", "random", "random_vibe"]
    },
    # 2. Cat Typing
    {
        "id": "cat_typing",
        "title": "Cat typing fast",
        "url": "/media/cat_typing.mp4",
        "preview_url": "/media/cat_typing.mp4",
        "tags": ["it", "it_deadline", "cat", "typing", "code", "work", "keyboard", "panic", "deadline", "study", "study_exam"]
    },
    # 3. Blinking Guy
    {
        "id": "blinking_guy",
        "title": "Drew Scanlon Blinking",
        "url": "/media/blinking_guy.mp4",
        "preview_url": "/media/blinking_guy.mp4",
        "tags": ["session", "study_exam", "exam", "confused", "what", "surprise", "blink", "it", "study", "cringe", "cringe_love", "random", "random_vibe"]
    },
    # 4. Travolta
    {
        "id": "travolta",
        "title": "Confused John Travolta",
        "url": "/media/travolta.mp4",
        "preview_url": "/media/travolta.mp4",
        "tags": ["cringe", "cringe_love", "confused", "session", "study_exam", "random", "random_vibe", "travolta", "lost", "where", "search"]
    },
    # 5. Pepe Crying
    {
        "id": "pepe_crying",
        "title": "Pepe crying emotional",
        "url": "/media/pepe_crying.mp4",
        "preview_url": "/media/pepe_crying.mp4",
        "tags": ["cringe", "cringe_love", "session", "study_exam", "crying", "sad", "tears", "pain", "regret", "exam", "it", "it_deadline"]
    },
    # 6. Mind Blown
    {
        "id": "mind_blown",
        "title": "Mind blown explosion",
        "url": "/media/mind_blown.mp4",
        "preview_url": "/media/mind_blown.mp4",
        "tags": ["smart", "brain", "think", "mind", "blown", "explosion", "shock", "it", "it_deadline", "session", "study_exam", "random", "random_vibe"]
    },
    # 7. Facepalm
    {
        "id": "facepalm",
        "title": "Facepalm annoyed",
        "url": "/media/facepalm.mp4",
        "preview_url": "/media/facepalm.mp4",
        "tags": ["cringe", "cringe_love", "facepalm", "cat", "annoyed", "stupid", "mistake", "fail", "it", "session"]
    },
    # 8. Keyboard Rage
    {
        "id": "keyboard_rage",
        "title": "Keyboard smash rage",
        "url": "/media/keyboard_rage.mp4",
        "preview_url": "/media/keyboard_rage.mp4",
        "tags": ["it", "it_deadline", "rage", "angry", "keyboard", "smash", "deadline", "bug", "computer", "session", "study_exam"]
    },
    # 9. Party Dance
    {
        "id": "party_dance",
        "title": "Carlton party dance",
        "url": "/media/party_dance.mp4",
        "preview_url": "/media/party_dance.mp4",
        "tags": ["friday", "friday_evening", "party", "dance", "happy", "weekend", "groove", "celebrate", "success", "money_success"]
    },
    # 10. Shiba Dance
    {
        "id": "shiba_dance",
        "title": "Shiba dog dance",
        "url": "/media/shiba_dance.mp4",
        "preview_url": "/media/shiba_dance.mp4",
        "tags": ["friday", "friday_evening", "party", "dance", "doge", "shiba", "weekend", "happy", "cute", "dog", "random", "random_vibe"]
    },
    # 11. Money Rain
    {
        "id": "money_rain",
        "title": "Make it rain cash",
        "url": "/media/money_rain.mp4",
        "preview_url": "/media/money_rain.mp4",
        "tags": ["money", "money_success", "cash", "rain", "rich", "salary", "boss", "dollars", "stonks", "success"]
    },
    # 12. Sleeping Cat
    {
        "id": "sleeping_cat",
        "title": "Sleeping cat tired",
        "url": "/media/sleeping_cat.mp4",
        "preview_url": "/media/sleeping_cat.mp4",
        "tags": ["friday", "friday_evening", "weekend", "sleep", "tired", "cat", "lazy", "bed", "night", "asleep", "chill"]
    },
    # 13. Office No
    {
        "id": "office_no",
        "title": "Michael Scott NO GOD NO",
        "url": "/media/office_no.mp4",
        "preview_url": "/media/office_no.mp4",
        "tags": ["it", "it_deadline", "deadline", "session", "study_exam", "cringe", "cringe_love", "no", "panic", "disaster", "yell"]
    },
    # 14. Shocked Pikachu
    {
        "id": "shocked_pikachu",
        "title": "Shocked Pikachu",
        "url": "/media/shocked_pikachu.mp4",
        "preview_url": "/media/shocked_pikachu.mp4",
        "tags": ["cringe", "cringe_love", "session", "study_exam", "exam", "what", "surprise", "pikachu", "shock", "random", "random_vibe"]
    },
    # 15. Success Kid
    {
        "id": "success_kid",
        "title": "Success Kid fist pump",
        "url": "/media/success_kid.mp4",
        "preview_url": "/media/success_kid.mp4",
        "tags": ["success", "money_success", "win", "victory", "passed", "done", "yes", "kid", "exam", "session", "study_exam"]
    },
    # 16. DiCaprio Laugh
    {
        "id": "dicaprio_laugh",
        "title": "DiCaprio Django laugh",
        "url": "/media/dicaprio_laugh.mp4",
        "preview_url": "/media/dicaprio_laugh.mp4",
        "tags": ["cringe", "cringe_love", "laugh", "dicaprio", "django", "evil", "smug", "joke", "friday", "friday_evening", "random", "random_vibe"]
    },
    # 17. Popcorn Eating
    {
        "id": "popcorn_eating",
        "title": "Popcorn eating drama",
        "url": "/media/popcorn_eating.mp4",
        "preview_url": "/media/popcorn_eating.mp4",
        "tags": ["cringe", "cringe_love", "popcorn", "drama", "eating", "watching", "chat", "show", "friday", "friday_evening", "random", "random_vibe"]
    },
    # 18. Spongebob Tired
    {
        "id": "spongebob_tired",
        "title": "SpongeBob exhausted tired",
        "url": "/media/spongebob_tired.mp4",
        "preview_url": "/media/spongebob_tired.mp4",
        "tags": ["it", "it_deadline", "session", "study_exam", "spongebob", "tired", "exhausted", "breath", "deadline", "exam", "done", "work"]
    },
    # 19. Pedro Raccoon
    {
        "id": "pedro_raccoon",
        "title": "Pedro Pedro raccoon",
        "url": "/media/pedro_raccoon.mp4",
        "preview_url": "/media/pedro_raccoon.mp4",
        "tags": ["friday", "friday_evening", "raccoon", "pedro", "dance", "party", "spinning", "happy", "weekend", "cute", "music", "random", "random_vibe"]
    },
    # 20. Steve Carell Crying
    {
        "id": "steve_carell_crying",
        "title": "Steve Carell crying emotional",
        "url": "/media/steve_carell_crying.mp4",
        "preview_url": "/media/steve_carell_crying.mp4",
        "tags": ["cringe", "cringe_love", "session", "study_exam", "it", "it_deadline", "carell", "crying", "office", "sad", "pain", "tears", "regret"]
    },
    # 21. Confused Anime (Is this a pigeon)
    {
        "id": "confused_anime",
        "title": "Is this a pigeon anime butterfly",
        "url": "/media/confused_anime.mp4",
        "preview_url": "/media/confused_anime.mp4",
        "tags": ["it", "it_deadline", "session", "study_exam", "cringe", "cringe_love", "anime", "butterfly", "pigeon", "confused", "question", "what", "bug"]
    },
    # 22. Success Borat
    {
        "id": "success_borat",
        "title": "Borat Great Success",
        "url": "/media/success_borat.mp4",
        "preview_url": "/media/success_borat.mp4",
        "tags": ["success", "money_success", "borat", "great", "thumbs", "win", "victory", "passed", "done", "exam", "approved"]
    },
    # 23. Cat Screaming
    {
        "id": "cat_screaming",
        "title": "Cat screaming panic",
        "url": "/media/cat_screaming.mp4",
        "preview_url": "/media/cat_screaming.mp4",
        "tags": ["it", "it_deadline", "session", "study_exam", "cat", "screaming", "scream", "panic", "fire", "deadline", "exam", "chaos"]
    },
    # 24. Cat Smack
    {
        "id": "cat_smack",
        "title": "Cat smack slap",
        "url": "/media/cat_smack.mp4",
        "preview_url": "/media/cat_smack.mp4",
        "tags": ["it", "it_deadline", "cringe", "cringe_love", "cat", "smack", "slap", "hit", "rage", "punch", "fight", "random", "random_vibe"]
    },
    # 25. Dance Club
    {
        "id": "dance_club",
        "title": "Club party dance rave",
        "url": "/media/dance_club.mp4",
        "preview_url": "/media/dance_club.mp4",
        "tags": ["friday", "friday_evening", "party", "dance", "club", "rave", "weekend", "lights", "groove", "celebrate"]
    },
    # 26. Money Pile
    {
        "id": "money_pile",
        "title": "Breaking Bad money pile",
        "url": "/media/money_pile.mp4",
        "preview_url": "/media/money_pile.mp4",
        "tags": ["money", "money_success", "success", "cash", "pile", "rich", "salary", "breaking", "bad", "huell", "dollars", "stonks"]
    },
    # 27. Brain Explode
    {
        "id": "brain_explode",
        "title": "Brain expanding cosmic explosion",
        "url": "/media/brain_explode.mp4",
        "preview_url": "/media/brain_explode.mp4",
        "tags": ["it", "it_deadline", "session", "study_exam", "brain", "explode", "mind", "blown", "smart", "galaxy", "idea", "genius"]
    },
    # 28. Clint Nod
    {
        "id": "clint_nod",
        "title": "Clint Eastwood nodding approval",
        "url": "/media/clint_nod.mp4",
        "preview_url": "/media/clint_nod.mp4",
        "tags": ["friday", "friday_evening", "success", "money_success", "nod", "nodding", "approval", "respect", "man", "beard", "passed", "good"]
    },
    # 29. Dog Typing
    {
        "id": "dog_typing",
        "title": "Dog typing on laptop",
        "url": "/media/dog_typing.mp4",
        "preview_url": "/media/dog_typing.mp4",
        "tags": ["it", "it_deadline", "session", "study_exam", "dog", "typing", "laptop", "work", "code", "coder", "programmer", "deadline", "homework"]
    },
    # 30. Deal With It
    {
        "id": "deal_with_it",
        "title": "Deal with it sunglasses",
        "url": "/media/deal_with_it.mp4",
        "preview_url": "/media/deal_with_it.mp4",
        "tags": ["success", "money_success", "deal", "glasses", "sunglasses", "cool", "boss", "swag", "win", "random", "random_vibe"]
    },
    # 31. Mind Blown Galaxy
    {
        "id": "mind_blown_galaxy",
        "title": "Galaxy mind blown space",
        "url": "/media/mind_blown_galaxy.mp4",
        "preview_url": "/media/mind_blown_galaxy.mp4",
        "tags": ["session", "study_exam", "it", "it_deadline", "random", "random_vibe", "galaxy", "space", "mind", "blown", "explosion", "universe", "shock"]
    },
    # 32. Shocked Fry
    {
        "id": "shocked_fry",
        "title": "Futurama Fry shocked squint",
        "url": "/media/shocked_fry.mp4",
        "preview_url": "/media/shocked_fry.mp4",
        "tags": ["cringe", "cringe_love", "session", "study_exam", "fry", "futurama", "shocked", "squint", "suspicious", "doubt", "what"]
    },
    # 33. Confused Math Lady
    {
        "id": "confused_math_lady",
        "title": "Confused math lady calculating",
        "url": "/media/confused_math_lady.mp4",
        "preview_url": "/media/confused_math_lady.mp4",
        "tags": ["session", "study_exam", "it", "it_deadline", "cringe", "cringe_love", "math", "calculating", "confused", "formula", "thinking", "exam", "what"]
    }
]

# Алиас для совместимости
FALLBACK_MEDIA_POOL = FALLBACK_MEMES


class MediaList(list):
    """Список медиа-результатов с поддержкой метаданных пагинации."""
    def __init__(self, items, next_pos: str = "", offset: int = 0, has_more: bool = True):
        super().__init__(items)
        self.next_pos = next_pos
        self.offset = offset
        self.has_more = has_more


def get_fallback_media(
    query: str = "",
    limit: int = 12,
    offset: int = 0,
    shuffle: bool = False
) -> MediaList:
    """Возвращает медиа из локального fallback-каталога (33+ клипа) с циклической пагинацией и перемешиванием."""
    q_lower = query.lower().strip() if query else ""
    q_words = set(q_lower.replace(",", " ").replace("-", " ").split())

    if q_lower and q_lower not in ("random", "all", "все"):
        scored = []
        for meme in FALLBACK_MEMES:
            tags = set(meme.get("tags", []))
            matches = len(q_words.intersection(tags))
            if any(q in t for q in q_words for t in tags):
                matches += 1
            if matches > 0:
                scored.append((matches, meme))

        scored.sort(key=lambda x: x[0], reverse=True)
        matched = [item for score, item in scored]
    else:
        matched = []

    if not matched:
        matched = FALLBACK_MEMES.copy()

    if shuffle:
        matched_copy = matched.copy()
        random.shuffle(matched_copy)
        matched = matched_copy

    total = len(matched)
    if total == 0:
        return MediaList([])

    start = offset % total
    if start + limit <= total:
        slice_items = matched[start : start + limit]
    else:
        slice_items = matched[start:] + matched[: (start + limit) - total]

    res = [
        {
            "id": it["id"],
            "title": it.get("title", "Meme"),
            "url": it["url"],
            "preview_url": it.get("preview_url", it["url"]),
            "is_fallback": True
        }
        for it in slice_items
    ]
    return MediaList(res, next_pos="", offset=offset + len(res), has_more=True)


async def search_media(
    query: str,
    limit: int = 12,
    offset: int = 0,
    pos: str = "",
    shuffle: bool = False,
    api_key: Optional[str] = None,
    timeout_sec: float = 6.0
) -> MediaList:
    """
    Поиск зацикленных видео-мемов (MP4/tinymp4):
    Использует Tenor API v2 с поддержкой pos/offset/shuffle, либо обращается к L1-кэшу и локальному пулу.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return get_fallback_media("", limit=limit, offset=offset, shuffle=shuffle)

    cache_key = f"{clean_query.lower()}:{offset}:{pos}:{shuffle}"
    now = time.time()

    # Проверка L1 кэша (только если не запрошен shuffle)
    if not shuffle and cache_key in _QUERY_CACHE:
        cached_time, cached_results = _QUERY_CACHE[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            logger.info(f"Tenor кэш HIT для '{clean_query}' ({len(cached_results)} шт.)")
            return cached_results

    actual_key = api_key or DEFAULT_TENOR_KEY or os.getenv("TENOR_API_KEY", "").strip()

    if not actual_key or actual_key == "YOUR_TENOR_API_KEY":
        return get_fallback_media(clean_query, limit=limit, offset=offset, shuffle=shuffle)

    encoded_query = urllib.parse.quote(clean_query)
    url = (
        f"https://tenor.googleapis.com/v2/search"
        f"?q={encoded_query}"
        f"&key={actual_key}"
        f"&client_key=vibe_stickers_app"
        f"&limit={min(limit, 25)}"
        f"&media_filter=tinymp4,nanomp4,mp4"
        f"&contentfilter=medium"
    )
    if pos:
        url += f"&pos={pos}"

    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    err_body = await resp.text()
                    logger.warning(f"Tenor API status {resp.status}: {err_body[:100]}. Fallback.")
                    return get_fallback_media(clean_query, limit=limit, offset=offset, shuffle=shuffle)

                data = await resp.json()
                next_pos = data.get("next", "")
                raw_results = data.get("results", [])
                results = []
                for item in raw_results:
                    formats = item.get("media_formats", {})
                    # Приоритет MP4 для быстрой конвертации в VP9
                    mp4_data = formats.get("tinymp4") or formats.get("nanomp4") or formats.get("mp4") or {}
                    gif_data = formats.get("tinygif") or formats.get("gif") or {}

                    video_url = mp4_data.get("url") or gif_data.get("url")
                    preview_url = gif_data.get("url") or video_url

                    if video_url:
                        results.append({
                            "id": item.get("id"),
                            "title": item.get("content_description", "Meme"),
                            "url": video_url,
                            "preview_url": preview_url,
                            "dims": mp4_data.get("dims") or [512, 512],
                            "is_fallback": False
                        })

                if not results:
                    return get_fallback_media(clean_query, limit=limit, offset=offset, shuffle=shuffle)

                if shuffle:
                    random.shuffle(results)

                media_list = MediaList(
                    results[:limit],
                    next_pos=next_pos,
                    offset=offset + len(results[:limit]),
                    has_more=bool(next_pos or len(results) >= limit)
                )

                if not shuffle:
                    _QUERY_CACHE[cache_key] = (now, media_list)
                return media_list

    except asyncio.TimeoutError:
        logger.warning(f"Таймаут Tenor API ({timeout_sec}s). Используется Fallback.")
        return get_fallback_media(clean_query, limit=limit, offset=offset, shuffle=shuffle)
    except Exception as e:
        logger.warning(f"Ошибка Tenor API: {e}. Используется Fallback.")
        return get_fallback_media(clean_query, limit=limit, offset=offset, shuffle=shuffle)


async def search_gifs(
    query: str,
    limit: int = 12,
    offset: int = 0,
    pos: str = "",
    shuffle: bool = False
) -> MediaList:
    """Алиас для search_media, совместимый с api/routes.py."""
    return await search_media(query=query, limit=limit, offset=offset, pos=pos, shuffle=shuffle)


async def ai_search_gifs_pipeline(
    query: str,
    limit: int = 12,
    offset: int = 0,
    pos: str = "",
    shuffle: bool = False
) -> Dict[str, Any]:
    """
    Интеллектуальный конвейер подбора гифок:
    1. Переводит русскоязычные или неточные запросы в семантические английские теги
       через Gemini Flash AI (или локальный эвристический маппинг).
    2. Генерирует остроумный мем-панчлайн (top/bottom text) и подходящий эмодзи.
    3. Ищет зацикленные видео/гифки в Tenor v2 или локальном пуле 33+ культовых мемов с поддержкой пагинации и shuffle.
    """
    clean_query = (query or "").strip()

    # 1. Семантический перевод и генерация панчлайна
    try:
        from core.gemini_client import ai_translate_query
        ai_res = await ai_translate_query(clean_query)
    except Exception as e:
        logger.warning(f"Ошибка ai_translate_query в pipeline: {e}")
        ai_res = {
            "search_query": clean_query or "funny meme",
            "top_text": clean_query.upper() if clean_query else "ЧИСТО МОЙ ВАЙБ",
            "bottom_text": "КОГДА ВСЁ ПОД КОНТРОЛЕМ",
            "emoji": "🔥",
            "is_ai": False
        }

    search_tag = ai_res.get("search_query") or clean_query or "funny meme"

    # 2. Поиск медиа по переведённым тегам с пагинацией
    gifs = await search_media(query=search_tag, limit=limit, offset=offset, pos=pos, shuffle=shuffle)

    # Если по специфичному тегу ничего не нашлось, пробуем оригинальный запрос или fallback
    if not gifs and search_tag != clean_query and clean_query:
        gifs = await search_media(query=clean_query, limit=limit, offset=offset, pos=pos, shuffle=shuffle)
    if not gifs:
        gifs = get_fallback_media("random", limit=limit, offset=offset, shuffle=shuffle)

    return {
        "status": "ok",
        "query": clean_query,
        "search_query": search_tag,
        "suggested_top": ai_res.get("top_text", ""),
        "suggested_bottom": ai_res.get("bottom_text", ""),
        "emoji": ai_res.get("emoji", "🔥"),
        "is_ai": ai_res.get("is_ai", False),
        "gifs": list(gifs),
        "next_pos": getattr(gifs, "next_pos", ""),
        "offset": offset + len(gifs),
        "has_more": getattr(gifs, "has_more", True)
    }

