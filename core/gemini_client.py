"""
Gemini Flash AI Client for Vibe and Punchline Generation.
Connects to Google Gemini API (via REST v1beta) or provides
a rich fallback catalog for offline / demo mode.
"""

import os
import json
import random
import logging
import asyncio
from typing import Dict, Any, Optional
import aiohttp

try:
    from bot.config import config
    DEFAULT_GEMINI_KEY = config.GEMINI_API_KEY
except Exception:
    DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

logger = logging.getLogger(__name__)

# Категории вайба
CATEGORIES = {
    "it_deadline": "Айти / Дедлайн / Баги на проде",
    "study_exam": "Сессия / Учеба / Зубрежка перед экзаменом",
    "friday_evening": "Пятница / Вечер / Долгожданный отдых",
    "cringe_love": "Отношения / Кринж / Неловкие ситуации",
    "money_success": "Деньги / Успех / Крах или богатство",
    "random_vibe": "Случайный вайб / Абсурдный постироничный юмор",
    "zoomer": "Зумерский сленг / ТикТок / Мемы",
    "dev": "IT / Разработка / Прогеры",
    "crypto": "Темщики / Крипта / Суета",
    "corporate": "Офис / Корпорат / Синк",
    "postirony": "Постирония / Абсурд",
}

# 5 ключевых стилей сленга для генерации
SLANG_STYLES = {
    "zoomer": {
        "id": "zoomer",
        "name": "⚡ Зум / ТикТок",
        "icon": "⚡",
        "keywords": ["база", "имба", "скуф", "альтушка", "сигма", "кринж", "рил", "чиназес", "жиза", "тяги", "тюбик"],
        "tone": "Используй сочный молодежный зумерский мемный сленг: 'БАЗА', 'ИМБА', 'СКУФ', 'АЛЬТУШКА', 'СИГМА', 'ЧИНАЗЕС', 'КРИНЖ', 'РИЛ', 'ТЮБИК', 'ТЯГИ', 'ЖИЗА'."
    },
    "dev": {
        "id": "dev",
        "name": "💻 IT & Dev",
        "icon": "💻",
        "keywords": ["прод", "костыль", "деплой", "легаси", "ревьюер", "таска", "созвон", "синьор", "баг", "фикс"],
        "tone": "Используй суровый айтишный и девелоперский сленг: 'ПРОД УПАЛ', 'КОСТЫЛЬ', 'ДЕПЛОЙ В ПЯТНИЦУ', 'ЛЕГАСИ', 'РЕВЬЮЕР ДУШИТ', 'ТАСКА ГОРИТ', 'СИНЬОР В СЛЕЗАХ'."
    },
    "crypto": {
        "id": "crypto",
        "name": "💸 Темщики / Крипта",
        "icon": "💸",
        "keywords": ["темка", "воркаем", "суета", "туземун", "ликвиднуло", "холдим", "не мамонт", "прибыль", "ракета"],
        "tone": "Используй дерзкий сленг темщиков, суетологов и криптанов: 'ВОРКАЕМ', 'ТЕМКА ЗАШЛА', 'СУЕТА', 'ТУЗЕМУН', 'ЛИКВИДНУЛО', 'ХОЛДИМ', 'НЕ МАМОНТ', 'ФИКСАНУЛ'."
    },
    "corporate": {
        "id": "corporate",
        "name": "🍷 Офис / Корпорат",
        "icon": "🍷",
        "keywords": ["синк", "услышал", "аппрув", "коллеги", "дедлайн", "созвон", "фидбек", "асап"],
        "tone": "Используй офисный пассивно-агрессивный корпоративный сленг: 'Я ВАС УСЛЫШАЛ', 'ДАВАЙТЕ СИНКНЕМСЯ', 'КОЛЛЕГИ, ДОБРЫЙ ДЕНЬ', 'ДЕДЛАЙН ВЧЕРА', 'АППРУВНИТЕ ТАСКУ'."
    },
    "postirony": {
        "id": "postirony",
        "name": "🗿 Постирония / Абсурд",
        "icon": "🗿",
        "keywords": ["понел", "волк", "думайте", "чилл", "бебра", "гигачад", "чисто я"],
        "tone": "Используй глубокую постиронию и мемный абсурд: 'ПОНЕЛ ЗРЯ БЫКАСАНУЛ', 'ВОЛК СЛАБЕЕ ЛЬВА', 'ДУМАЙТЕ', 'ЧИЛЛ', 'БЕБРА', 'ЧИСТО Я', 'ГИГАЧАД'."
    }
}

# Синонимы и алиасы для маппинга входящих категорий
CATEGORY_ALIASES = {
    "it": "dev",
    "deadline": "dev",
    "айти": "dev",
    "дедлайн": "dev",
    "прод": "dev",
    "dev": "dev",
    "zoomer": "zoomer",
    "зум": "zoomer",
    "зумер": "zoomer",
    "tiktok": "zoomer",
    "crypto": "crypto",
    "крипта": "crypto",
    "темщик": "crypto",
    "темка": "crypto",
    "corporate": "corporate",
    "офис": "corporate",
    "корпорат": "corporate",
    "postirony": "postirony",
    "постирония": "postirony",
    "абсурд": "postirony",
    "session": "study_exam",
    "study": "study_exam",
    "exam": "study_exam",
    "сессия": "study_exam",
    "учеба": "study_exam",
    "экзамен": "study_exam",
    "friday": "friday_evening",
    "пятница": "friday_evening",
    "вечер": "friday_evening",
    "отдых": "friday_evening",
    "cringe": "cringe_love",
    "love": "cringe_love",
    "кринж": "cringe_love",
    "отношения": "cringe_love",
    "любовь": "cringe_love",
    "money": "crypto",
    "success": "crypto",
    "деньги": "crypto",
    "успех": "crypto",
    "богатство": "crypto",
    "random": "random_vibe",
    "случайный": "random_vibe",
    "рандом": "random_vibe",
    "all": "random_vibe",
    "любой": "random_vibe",
}

# Каталог готовых мем-вайбов для оффлайн/демо-режима
FALLBACK_VIBES: Dict[str, list] = {
    "it_deadline": [
        {
            "punchline": "РАБОТАЕТ? НЕ ТРОГАЙ!",
            "top_text": "ДЕПЛОЙ В ПЯТНИЦУ В 18:00",
            "bottom_text": "И ТАК СОЙДЁТ",
            "search_query": "fire disaster explosion cat",
            "gif_query": "fire disaster explosion cat",
            "emoji": "🔥"
        },
        {
            "punchline": "КОГДА ПОФИКСИЛ ОДИН БАГ, А ВЫЛЕЗЛО ДЕСЯТЬ",
            "top_text": "КОГДА ПОФИКСИЛ ОДИН БАГ",
            "bottom_text": "ПОЯВИЛОСЬ СЕМЬ НОВЫХ",
            "search_query": "confused programmer typing panic",
            "gif_query": "confused programmer typing panic",
            "emoji": "💻"
        },
        {
            "punchline": "РАБОТАЕТ НА МОЁМ КОМПЬЮТЕРЕ",
            "top_text": "РАБОТАЕТ НА МОЁМ ПК",
            "bottom_text": "ПРОБЛЕМА НА ТВОЕЙ СТОРОНЕ",
            "search_query": "smug shrug smile whatever",
            "gif_query": "smug shrug smile whatever",
            "emoji": "🤷‍♂️"
        },
        {
            "punchline": "ТАМ ПРАВОК НА 5 МИНУТ (ДЕЛАЕМ ТРЕТЬЮ НЕДЕЛЮ)",
            "top_text": "PM: ТАМ ПРАВОК НА 5 МИНУТ",
            "bottom_text": "ДЕЛАЕМ ТРЕТЬЮ НЕДЕЛЮ",
            "search_query": "tired skeleton crying desk",
            "gif_query": "tired skeleton crying desk",
            "emoji": "💀"
        },
        {
            "punchline": "ЗАКРЫЛ ТИКЕТ БЕЗ ТЕСТОВ",
            "top_text": "ЗАКРЫЛ ТИКЕТ",
            "bottom_text": "ТЕСТЫ ДЛЯ СЛАБАКОВ",
            "search_query": "homer simpson bush disappear",
            "gif_query": "homer simpson bush disappear",
            "emoji": "🤡"
        },
        {
            "punchline": "СОЗВОН, КОТОРЫЙ МОГ БЫТЬ ОДНИМ ПИСЬМОМ",
            "top_text": "ЧАСОВОЙ СОЗВОН",
            "bottom_text": "МОГ БЫТЬ ОДНИМ ПИСЬМОМ",
            "search_query": "falling asleep boring meeting",
            "gif_query": "falling asleep boring meeting",
            "emoji": "😴"
        }
    ],
    "study_exam": [
        {
            "punchline": "ДО ЭКЗАМЕНА 3 ЧАСА: НАЧИНАЮ УЧИТЬ АЛФАВИТ",
            "top_text": "ДО ЭКЗАМЕНА 3 ЧАСА",
            "bottom_text": "НАЧИНАЮ УЧИТЬ АЛФАВИТ",
            "search_query": "student studying panic crying speed reading",
            "gif_query": "student studying panic crying speed reading",
            "emoji": "📚"
        },
        {
            "punchline": "БИЛЕТ ПОПАЛСЯ ТОТ САМЫЙ, КОТОРЫЙ НЕ УЧИЛ",
            "top_text": "БИЛЕТ ПОПАЛСЯ ТОТ САМЫЙ",
            "bottom_text": "КОТОРЫЙ Я НЕ УЧИЛ",
            "search_query": "stare silence shock moai",
            "gif_query": "stare silence shock moai",
            "emoji": "🗿"
        },
        {
            "punchline": "СДАЛ НА ТРОЙКУ И СЧАСТЛИВ",
            "top_text": "ТРОЙКА В ЗАЧЕТКЕ",
            "bottom_text": "ПРАЗДНУЕМ КАК ДИПЛОМ",
            "search_query": "victory dance jumping celebration",
            "gif_query": "victory dance jumping celebration",
            "emoji": "🥳"
        },
        {
            "punchline": "ПОСПАЛ 2 ЧАСА ПЕРЕД СЕССИЕЙ",
            "top_text": "СОН ДЛЯ СЛАБЫХ",
            "bottom_text": "ГЛАЗА ПОКИНУЛИ ЧАТ",
            "search_query": "zombie walking tired exhausted",
            "gif_query": "zombie walking tired exhausted",
            "emoji": "🧟"
        }
    ],
    "friday_evening": [
        {
            "punchline": "ПЯТНИЦА 18:00: УЖЕ МЕНТАЛЬНО В БАРЕ",
            "top_text": "ПЯТНИЦА 17:59",
            "bottom_text": "УЖЕ МЕНТАЛЬНО В БАРЕ",
            "search_query": "happy dance weekend party cheers",
            "gif_query": "happy dance weekend party cheers",
            "emoji": "🍻"
        },
        {
            "punchline": "ШЕФ: ЕСТЬ СРОЧНАЯ ЗАДАЧА. Я: АБОНЕНТ ВНЕ ЗОНЫ",
            "top_text": "ШЕФ: ЕСТЬ СРОЧНАЯ ЗАДАЧА",
            "bottom_text": "АБОНЕНТ ВНЕ ЗОНЫ ДОСТУПА",
            "search_query": "running away fast smoke sprint",
            "gif_query": "running away fast smoke sprint",
            "emoji": "🏃‍♂️"
        },
        {
            "punchline": "ПЛАНЫ НА ВЫХОДНЫЕ: СПАТЬ 48 ЧАСОВ",
            "top_text": "ПЛАНЫ НА ВЫХОДНЫЕ",
            "bottom_text": "СПАТЬ 48 ЧАСОВ ПОДРЯД",
            "search_query": "sleeping cat cozy bed lazy",
            "gif_query": "sleeping cat cozy bed lazy",
            "emoji": "😴"
        },
        {
            "punchline": "ВХОЖУ В РЕЖИМ ВЫХОДНОГО ДНЯ",
            "top_text": "РЕЖИМ ВЫХОДНЫХ",
            "bottom_text": "УСПЕШНО АКТИВИРОВАН",
            "search_query": "dancing grooving happy weekend",
            "gif_query": "dancing grooving happy weekend",
            "emoji": "🕺"
        }
    ],
    "cringe_love": [
        {
            "punchline": "ВСПОМНИЛ СВОИ СООБЩЕНИЯ ТРЁХЛЕТНЕЙ ДАВНОСТИ",
            "top_text": "ВСПОМНИЛ СВОИ СООБЩЕНИЯ",
            "bottom_text": "ТРЁХЛЕТНЕЙ ДАВНОСТИ",
            "search_query": "facepalm cringe looking away awkward",
            "gif_query": "facepalm cringe looking away awkward",
            "emoji": "🙈"
        },
        {
            "punchline": "ПОЗДОРОВАЛСЯ С ЧЕЛОВЕКОМ, КОТОРЫЙ МАХАЛ НЕ МНЕ",
            "top_text": "ПОЗДОРОВАЛСЯ С ЧЕЛОВЕКОМ",
            "bottom_text": "КОТОРЫЙ МАХАЛ НЕ МНЕ",
            "search_query": "awkward disappearing hedge homer",
            "gif_query": "awkward disappearing hedge homer",
            "emoji": "🚶‍♂️"
        },
        {
            "punchline": "СКАЗАЛ 'СПАСИБО И ВАМ' ОФИЦИАНТУ",
            "top_text": "ОФИЦИАНТ: ПРИЯТНОГО АППЕТИТА",
            "bottom_text": "Я: СПАСИБО И ВАМ",
            "search_query": "clown mask realization regret",
            "gif_query": "clown mask realization regret",
            "emoji": "🤡"
        },
        {
            "punchline": "ОНА СКАЗАЛА: ТЫ МНЕ КАК БРАТ",
            "top_text": "ФРЕНДЗОНА",
            "bottom_text": "ТЫ МНЕ КАК БРАТИК",
            "search_query": "heartbreak crying rain sad",
            "gif_query": "heartbreak crying rain sad",
            "emoji": "💔"
        }
    ],
    "money_success": [
        {
            "punchline": "ИНВЕСТИРОВАЛ 100 РУБЛЕЙ — БАЛАНС: 101 РУБЛЬ",
            "top_text": "ИНВЕСТИРОВАЛ 100 РУБЛЕЙ",
            "bottom_text": "БАЛАНС: 101 РУБЛЬ",
            "search_query": "stonks wolf of wall street cool",
            "gif_query": "stonks wolf of wall street cool",
            "emoji": "📈"
        },
        {
            "punchline": "СДЕЛАЛ ВИД, ЧТО РАЗБИРАЮСЬ, И ОНО СРАБОТАЛО",
            "top_text": "СДЕЛАЛ ВИД ЧТО ЗНАЮ",
            "bottom_text": "И ОНО СРАБОТАЛО",
            "search_query": "cool sunglasses walk deal with it",
            "gif_query": "cool sunglasses walk deal with it",
            "emoji": "😎"
        },
        {
            "punchline": "КУПИЛ НА ХАЯХ, ПРОКАТИЛСЯ НА СЕДОМ",
            "top_text": "КРИПТО-ИНВЕСТОР",
            "bottom_text": "КУПИЛ НА САМЫХ ХАЯХ",
            "search_query": "crypto chart crashing falling panic",
            "gif_query": "crypto chart crashing falling panic",
            "emoji": "📉"
        },
        {
            "punchline": "СИНДРОМ БОГАТОГО ЧЕЛОВЕКА В ДЕНЬ ЗАРПЛАТЫ",
            "top_text": "ДЕНЬ ЗАРПЛАТЫ",
            "bottom_text": "ГУЛЯЕМ НА ВСЕ ДЕНЬГИ",
            "search_query": "throwing money rain rich boss",
            "gif_query": "throwing money rain rich boss",
            "emoji": "💸"
        }
    ],
    "random_vibe": [
        {
            "punchline": "ПОНЕЛ ЗРЯ БЫКАСАНУЛ",
            "top_text": "ПОНЕЛ",
            "bottom_text": "ЗРЯ БЫКАСАНУЛ",
            "search_query": "moai stone regret silence",
            "gif_query": "moai stone regret silence",
            "emoji": "🗿"
        },
        {
            "punchline": "СИТУАЦИЯ СЛОЖНАЯ, НО МЫ РАЗБИРАЕМСЯ",
            "top_text": "СИТУАЦИЯ СЛОЖНАЯ",
            "bottom_text": "НО МЫ РАЗБИРАЕМСЯ",
            "search_query": "cat thinking detective glass",
            "gif_query": "cat thinking detective glass",
            "emoji": "🧐"
        },
        {
            "punchline": "Я ВАС УСЛЫШАЛ И ПРОИГНОРИРОВАЛ",
            "top_text": "Я ВАС УСЛЫШАЛ",
            "bottom_text": "И ПРОИГНОРИРОВАЛ",
            "search_query": "thumbs up smile nodding fake",
            "gif_query": "thumbs up smile nodding fake",
            "emoji": "👌"
        },
        {
            "punchline": "ВСЁ ПОД КОНТРОЛЕМ (НЕТ)",
            "top_text": "ВСЁ ПОД КОНТРОЛЕМ",
            "bottom_text": "СИТУАЦИЯ СТАБИЛЬНА (НЕТ)",
            "search_query": "dog this is fine fire room",
            "gif_query": "dog this is fine fire room",
            "emoji": "☕"
        }
    ],
    "zoomer": [
        {
            "punchline": "ЭТО БАЗА, ДРУГОГО НЕ ДАНО",
            "top_text": "ЭТО БАЗА",
            "bottom_text": "ИМБА И ТОЧКА",
            "search_query": "gigachad chad smile nod",
            "gif_query": "gigachad chad smile nod",
            "emoji": "🗿"
        },
        {
            "punchline": "ЧИНАЗЕС, СЮДА ЭТИ БАРХАТНЫЕ ТЯГИ",
            "top_text": "ЧИНАЗЕС",
            "bottom_text": "СЮДА ЭТИ БАРХАТНЫЕ ТЯГИ",
            "search_query": "shoes dance fancy happy",
            "gif_query": "shoes dance fancy happy",
            "emoji": "👞"
        },
        {
            "punchline": "ЧИСТО СКУФ В ПОИСКАХ АЛЬТУШКИ",
            "top_text": "ЧИСТО СКУФ",
            "bottom_text": "В ПОИСКАХ АЛЬТУШКИ",
            "search_query": "shrek mirror meme funny",
            "gif_query": "shrek mirror meme funny",
            "emoji": "🧌"
        },
        {
            "punchline": "СИГМА ВАЙБ В 3 ЧАСА НОЧИ",
            "top_text": "СИГМА ВАЙБ",
            "bottom_text": "МОЛЧА ДЕЛАЮ ДЕЛА",
            "search_query": "patrick bateman listening music walking",
            "gif_query": "patrick bateman listening music walking",
            "emoji": "🎧"
        },
        {
            "punchline": "РИЛ ЖИЗА БЕЗ КРИНЖА",
            "top_text": "РИЛ ЖИЗА",
            "bottom_text": "БЕЗ ЛИШНЕГО КРИНЖА",
            "search_query": "nodding cat rhythm cool",
            "gif_query": "nodding cat rhythm cool",
            "emoji": "🐱"
        }
    ],
    "dev": [
        {
            "punchline": "ПРОД УПАЛ, СИНЬОР В СЛЕЗАХ",
            "top_text": "ПРОД УПАЛ",
            "bottom_text": "СИНЬОР В СЛЕЗАХ",
            "search_query": "fire disaster explosion cat",
            "gif_query": "fire disaster explosion cat",
            "emoji": "🔥"
        },
        {
            "punchline": "ОДИН КОСТЫЛЬ ДЕРЖИТ ВЕСЬ БИЗНЕС",
            "top_text": "ОДИН КОСТЫЛЬ",
            "bottom_text": "ДЕРЖИТ ВЕСЬ БИЗНЕС",
            "search_query": "jenga tower falling balance",
            "gif_query": "jenga tower falling balance",
            "emoji": "🪵"
        },
        {
            "punchline": "РЕВЬЮЕР ДУШИТ ТРЕТИЙ ДЕНЬ",
            "top_text": "РЕВЬЮЕР ДУШИТ",
            "bottom_text": "ПРИДИРКА К ПРОБЕЛАМ",
            "search_query": "nerd glasses talking boring",
            "gif_query": "nerd glasses talking boring",
            "emoji": "🤓"
        },
        {
            "punchline": "GIT PUSH --FORCE И УДАЛИЛ ТЕЛЕГРАМ",
            "top_text": "GIT PUSH --FORCE",
            "bottom_text": "И УДАЛИЛ ТЕЛЕГРАМ",
            "search_query": "running away fast smoke",
            "gif_query": "running away fast smoke",
            "emoji": "🏃‍♂️"
        }
    ],
    "crypto": [
        {
            "punchline": "ТЕМКА ЗАШЛА, СУЕТА НА МИЛЛИОН",
            "top_text": "ТЕМКА ЗАШЛА",
            "bottom_text": "СУЕТА НА МИЛЛИОН",
            "search_query": "wolf of wall street clapping money",
            "gif_query": "wolf of wall street clapping money",
            "emoji": "💸"
        },
        {
            "punchline": "ЛИКВИДНУЛО В НОЛЬ, ХОЛДИМ ДО ТАЛОГО",
            "top_text": "ЛИКВИДНУЛО В НОЛЬ",
            "bottom_text": "ХОЛДИМ ДО ТАЛОГО",
            "search_query": "pepe crying depression rain",
            "gif_query": "pepe crying depression rain",
            "emoji": "📉"
        },
        {
            "punchline": "ТУЗЕМУН ОТМЕНИЛСЯ, РЕЗЮМЕ НА ЗАВОД",
            "top_text": "ТУЗЕМУН ОТМЕНИЛСЯ",
            "bottom_text": "РЕЗЮМЕ НА ЗАВОД ГОТОВО",
            "search_query": "worker hard hat tired",
            "gif_query": "worker hard hat tired",
            "emoji": "🏭"
        },
        {
            "punchline": "НЕ МАМОНТ, ЗАТО С ОПЫТОМ",
            "top_text": "НЕ МАМОНТ",
            "bottom_text": "ЗАТО С ОПЫТОМ",
            "search_query": "clown putting makeup mirror",
            "gif_query": "clown putting makeup mirror",
            "emoji": "🤡"
        }
    ],
    "corporate": [
        {
            "punchline": "Я ВАС УСЛЫШАЛ И ВЫБРОСИЛ",
            "top_text": "Я ВАС УСЛЫШАЛ",
            "bottom_text": "СПАСИБО ЗА ВАШЕ МНЕНИЕ",
            "search_query": "fake smile nodding dead eyes",
            "gif_query": "fake smile nodding dead eyes",
            "emoji": "🙃"
        },
        {
            "punchline": "ДАВАЙТЕ СИНКНЕМСЯ НА СОЗВОН О СОЗВОНЕ",
            "top_text": "ДАВАЙТЕ СИНКНЕМСЯ",
            "bottom_text": "ЧТОБЫ НАЗНАЧИТЬ СОЗВОН",
            "search_query": "bored office meeting sleeping",
            "gif_query": "bored office meeting sleeping",
            "emoji": "🥱"
        },
        {
            "punchline": "КОЛЛЕГИ, ДЕДЛАЙН СГОРЕЛ ВЧЕРА",
            "top_text": "ДОБРЫЙ ДЕНЬ, КОЛЛЕГИ",
            "bottom_text": "ДЕДЛАЙН СГОРЕЛ ВЧЕРА",
            "search_query": "skeleton typing desk waiting",
            "gif_query": "skeleton typing desk waiting",
            "emoji": "💀"
        },
        {
            "punchline": "АППРУВНИТЕ ТАСКУ, ПЯТНИЦА 17:59",
            "top_text": "АППРУВНИТЕ ТАСКУ",
            "bottom_text": "ПЯТНИЦА 17:59",
            "search_query": "praying hands please begging",
            "gif_query": "praying hands please begging",
            "emoji": "🙏"
        }
    ],
    "postirony": [
        {
            "punchline": "ПОНЕЛ ЗРЯ БЫКАСАНУЛ",
            "top_text": "ПОНЕЛ",
            "bottom_text": "ЗРЯ БЫКАСАНУЛ",
            "search_query": "moai stone regret silence",
            "gif_query": "moai stone regret silence",
            "emoji": "🗿"
        },
        {
            "punchline": "ВОЛК СЛАБЕЕ ЛЬВА, ДУМАЙТЕ",
            "top_text": "ВОЛК СЛАБЕЕ ЛЬВА",
            "bottom_text": "ДУМАЙТЕ",
            "search_query": "wolf moon howling deep",
            "gif_query": "wolf moon howling deep",
            "emoji": "🐺"
        },
        {
            "punchline": "ЧИСТО ЧИЛЛ, ХОТЯ ДОМ ГОРИТ",
            "top_text": "ЧИСТО ЧИЛЛ",
            "bottom_text": "ХОТЯ ДОМ ГОРИТ",
            "search_query": "dog this is fine burning coffee",
            "gif_query": "dog this is fine burning coffee",
            "emoji": "☕"
        },
        {
            "punchline": "БЕБРА МОМЕНТ 10 ИЗ 10",
            "top_text": "БЕБРА МОМЕНТ",
            "bottom_text": "ЧИСТО Я В ПОНЕДЕЛЬНИК",
            "search_query": "spinning dancing hamster",
            "gif_query": "spinning dancing hamster",
            "emoji": "🐹"
        }
    ]
}

# Поддержка коротких алиасов в словаре
FALLBACK_VIBES["it"] = FALLBACK_VIBES["dev"]
FALLBACK_VIBES["session"] = FALLBACK_VIBES["study_exam"]
FALLBACK_VIBES["friday"] = FALLBACK_VIBES["friday_evening"]
FALLBACK_VIBES["cringe"] = FALLBACK_VIBES["cringe_love"]
FALLBACK_VIBES["success"] = FALLBACK_VIBES["crypto"]
FALLBACK_VIBES["money"] = FALLBACK_VIBES["crypto"]
FALLBACK_VIBES["random"] = FALLBACK_VIBES["random_vibe"]


def normalize_category(category: str) -> str:
    """Нормализует категорию."""
    if not category:
        return "random_vibe"
    cat_lower = category.strip().lower()
    if cat_lower in CATEGORIES:
        return cat_lower
    if cat_lower in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cat_lower]
    if "random" in cat_lower or "рандом" in cat_lower or cat_lower == "all":
        return random.choice(list(CATEGORIES.keys()))
    return "random_vibe"


def get_fallback_vibe(
    category: str = "all",
    slang_style: str = "zoomer",
    custom_context: str = ""
) -> Dict[str, Any]:
    """Возвращает проверенный вайб из оффлайн-каталога с учетом сленга и кастомного контекста."""
    pool_key = None
    if slang_style and slang_style in FALLBACK_VIBES:
        pool_key = slang_style
    elif category and category.lower() in FALLBACK_VIBES:
        pool_key = category.lower()
    else:
        norm_key = normalize_category(category)
        pool_key = norm_key if norm_key in FALLBACK_VIBES else "random_vibe"

    items = FALLBACK_VIBES.get(pool_key) or FALLBACK_VIBES["random_vibe"]
    selected = random.choice(items).copy()

    top_text = selected.get("top_text") or ""
    bottom_text = selected.get("bottom_text") or selected.get("punchline") or "МЕМНЫЙ ВАЙБ"

    # Если пользователь передал локальные шутки или контекст чата
    if custom_context and custom_context.strip():
        ctx_word = custom_context.strip().upper()
        if len(ctx_word) > 25:
            ctx_word = ctx_word[:25]
        top_text = f"КОГДА {ctx_word}"
        punchline = f"{top_text}: {bottom_text}"
    else:
        punchline = selected.get("punchline") or f"{top_text} {bottom_text}".strip()

    search_query = selected.get("search_query") or selected.get("gif_query") or "funny meme reaction"
    emoji = selected.get("emoji") or "🔥"

    return {
        "punchline": punchline,
        "search_query": search_query,
        "emoji": emoji,
        "top_text": top_text,
        "bottom_text": bottom_text,
        "gif_query": search_query,
        "category": pool_key,
        "slang_style": slang_style,
        "is_fallback": True
    }


async def generate_vibe_ai(
    prompt: str = "",
    category: str = "all",
    slang_style: str = "zoomer",
    custom_context: str = "",
    api_key: Optional[str] = None,
    timeout_sec: float = 4.0
) -> Dict[str, Any]:
    """Генерация через официальный REST API Google Gemini 1.5 Flash с поддержкой сленга и контекста."""
    actual_key = api_key or DEFAULT_GEMINI_KEY or os.getenv("GEMINI_API_KEY", "").strip()
    if not actual_key or actual_key == "YOUR_GEMINI_API_KEY":
        raise ValueError("GEMINI_API_KEY не установлен.")

    norm_category = normalize_category(category)
    category_desc = CATEGORIES.get(norm_category, "Случайный мемный вайб")

    slang_info = SLANG_STYLES.get(slang_style, SLANG_STYLES["zoomer"])
    slang_tone = slang_info["tone"]

    custom_context_instruction = ""
    if custom_context and custom_context.strip():
        custom_context_instruction = (
            f" ОБЯЗАТЕЛЬНО учти локальный контекст/шутки пользователя: '{custom_context.strip()}'. "
            "Используй слова или тему из этого контекста в панчлайне!"
        )

    system_instruction = (
        "Ты — генератор коротких, смешных и вирусных мем-стикеров для Telegram. "
        f"Стиль и тональность речи: {slang_tone}."
        f"{custom_context_instruction} "
        f"Категория вайба: {category_desc}. "
        "Сгенерируй короткую панч-фразу (до 5-7 слов CAPS), верхний и нижний текст, эмодзи и 2-3 ключевых слова "
        "на английском для поиска видеомема на Tenor (описывай действие, реакцию или персонажа). "
        "Ответ верни СТРОГО в формате JSON:\n"
        "{\n"
        '  "punchline": "КОРОТКАЯ ПАНЧ-ФРАЗА",\n'
        '  "top_text": "ВЕРХНИЙ ТЕКСТ",\n'
        '  "bottom_text": "НИЖНИЙ ТЕКСТ",\n'
        '  "emoji": "🔥",\n'
        '  "search_query": "cat typing panic"\n'
        "}"
    )

    user_query = f"Тема: {category_desc}. Сленг: {slang_info['name']}. Контекст от пользователя: {prompt or custom_context or 'сгенерируй случайный популярный мем'}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction},
                    {"text": user_query}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.88,
            "responseMimeType": "application/json",
            "response_mime_type": "application/json"
        }
    }

    models_to_try = ["gemini-3-flash-preview", "gemini-flash-latest"]
    last_err = None

    timeout = aiohttp.ClientTimeout(total=timeout_sec)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={actual_key}"
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        last_err = f"Gemini API ({model_name}) error {resp.status}: {text[:100]}"
                        continue
                    data = await resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)

                    punchline = str(parsed.get("punchline") or parsed.get("bottom_text") or "").strip().upper()
                    top_text = str(parsed.get("top_text") or "").strip().upper()
                    bottom_text = str(parsed.get("bottom_text") or punchline).strip().upper()
                    search_query = str(parsed.get("search_query") or parsed.get("gif_query") or "meme reaction").strip()
                    emoji = str(parsed.get("emoji") or "🔥").strip()

                    if not punchline:
                        punchline = f"{top_text} {bottom_text}".strip() or "МЕМНЫЙ ВАЙБ"

                    return {
                        "punchline": punchline,
                        "search_query": search_query,
                        "emoji": emoji,
                        "top_text": top_text,
                        "bottom_text": bottom_text,
                        "gif_query": search_query,
                        "category": norm_category,
                        "slang_style": slang_style,
                        "is_fallback": False
                    }
            except Exception as e:
                last_err = str(e)
                continue

    raise RuntimeError(last_err or "Все модели Gemini недоступны.")


async def generate_vibe(
    category: str = "random",
    custom_prompt: str = "",
    prompt: str = "",
    slang_style: str = "zoomer",
    custom_context: str = "",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Основная функция генерации вайба с поддержкой сленга:
    Пытается вызвать Gemini Flash API, при отсутствии ключа или ошибке
    бесшовно возвращает вайб из встроенного сленгового каталога.
    """
    user_prompt = (custom_prompt or prompt or "").strip()
    actual_key = api_key or DEFAULT_GEMINI_KEY or os.getenv("GEMINI_API_KEY", "").strip()

    if actual_key and actual_key != "YOUR_GEMINI_API_KEY":
        try:
            return await generate_vibe_ai(
                prompt=user_prompt,
                category=category,
                slang_style=slang_style,
                custom_context=custom_context,
                api_key=actual_key
            )
        except Exception as e:
            logger.warning(f"Ошибка Gemini Flash API: {e}. Используем Fallback каталог.")

    return get_fallback_vibe(category=category, slang_style=slang_style, custom_context=custom_context)


# ==============================================================================
# AI GIF Search & Semantic Query Translation
# ==============================================================================

RUSSIAN_TO_TENOR_TAGS: Dict[str, str] = {
    "кот": "cat typing panic funny",
    "котик": "cute cat typing",
    "кошк": "cat screaming panic",
    "собак": "dog this is fine burning coffee",
    "пес": "dog typing laptop",
    "дедлайн": "deadline panic typing work emergency",
    "программист": "programmer typing panic computer code",
    "айти": "programmer coding computer bug",
    "код": "programmer coding keyboard bug",
    "баг": "programmer bug panic fix",
    "прод": "deploy friday fire panic",
    "пятниц": "friday party dance drink celebration",
    "тусовк": "party dance happy celebration club",
    "работ": "office work tired typing",
    "устал": "tired exhausted sleeping desk",
    "сон": "sleeping tired cat bed",
    "спать": "sleeping tired cat bed",
    "сесси": "student exam study panic",
    "экзамен": "exam study stress panic confused",
    "препод": "teacher professor lecture funny math",
    "учеб": "study homework tired student",
    "деньг": "money rich rain cash boss flex",
    "богат": "money rich boss flex pile",
    "зарплат": "money cash happy rich salary",
    "кринж": "cringe facepalm awkward silence mistake",
    "шок": "shocked surprise open mouth gasp mind blown",
    "паник": "panic run scream explosion cat",
    "огонь": "fire burning disaster this is fine dog",
    "слез": "crying emotional tears sad pepe",
    "груст": "sad crying pepe alone pain",
    "плач": "crying emotional tears sad steve carell",
    "ржака": "laughing laughter hysterical lol dicaprio",
    "смех": "laughing dicaprio funny borat",
    "мем": "funny meme reaction travolta",
    "любов": "love cringe heart cute",
    "курю": "smoke coffee tired waiting",
    "жду": "waiting travolta confused where",
}


async def ai_translate_query(
    query: str,
    api_key: Optional[str] = None,
    timeout_sec: float = 4.0
) -> Dict[str, Any]:
    """
    Анализирует пользовательский поисковый запрос через Gemini Flash AI:
    - Переводит разговорный запрос на русском/любом языке в 2-4 английских тега для Tenor API.
    - Генерирует остроумный мем-текст (сетап + панчлайн).
    - Подбирает эмодзи.
    - В случае недоступности AI использует локальный словарь соответствий.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "search_query": "funny meme reaction",
            "top_text": "ЧИСТО МОЙ ВАЙБ",
            "bottom_text": "КОГДА ВСЁ ПОД КОНТРОЛЕМ",
            "emoji": "🔥",
            "is_ai": False
        }

    actual_key = api_key or DEFAULT_GEMINI_KEY or os.getenv("GEMINI_API_KEY", "").strip()

    if actual_key and actual_key != "YOUR_GEMINI_API_KEY":
        system_instruction = (
            "Ты — ИИ-помощник генератора мем-стикеров для Telegram. "
            "Пользователь ищет мем или видео-фон по запросу (возможно на русском языке). "
            "Твоя задача: "
            "1. Переведи образ в 2-4 точных английских поисковых слова для Tenor/Giphy "
            "(только суть: персонаж, эмоция, действие, например: 'cat typing flames panic', 'crying student desk'). "
            "2. Придумай короткий остроумный мем-текст в тему запроса (top_text и bottom_text до 4-6 слов CAPS). "
            "3. Подбери подходящий эмодзи. "
            "Верни СТРОГО JSON без markdown:\n"
            "{\n"
            '  "search_query": "cat typing flames panic",\n'
            '  "top_text": "ВЕРХНИЙ ТЕКСТ",\n'
            '  "bottom_text": "НИЖНИЙ ТЕКСТ",\n'
            '  "emoji": "🔥"\n'
            "}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_instruction},
                        {"text": f"Запрос пользователя: {clean_query}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.75,
                "responseMimeType": "application/json"
            }
        }

        models_to_try = ["gemini-3-flash-preview", "gemini-flash-latest"]
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model_name in models_to_try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={actual_key}"
                    try:
                        async with session.post(url, json=payload) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                                parsed = json.loads(raw_text)
                                sq = str(parsed.get("search_query") or clean_query).strip()
                                top = str(parsed.get("top_text") or clean_query.upper()).strip()
                                bottom = str(parsed.get("bottom_text") or "").strip()
                                emoji = str(parsed.get("emoji") or "🔥").strip()
                                return {
                                    "search_query": sq,
                                    "top_text": top,
                                    "bottom_text": bottom,
                                    "emoji": emoji,
                                    "is_ai": True
                                }
                    except Exception as e:
                        logger.debug(f"Gemini model {model_name} search prompt error: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Ошибка Gemini AI Search: {e}. Используем локальный Fallback.")

    # Локальный Fallback по русским корням
    q_words = clean_query.lower().split()
    matched_tags = []
    for word in q_words:
        for ru_key, en_tags in RUSSIAN_TO_TENOR_TAGS.items():
            if ru_key in word:
                matched_tags.append(en_tags)
                break

    fallback_search = " ".join(matched_tags) if matched_tags else clean_query
    return {
        "search_query": fallback_search or "funny meme reaction",
        "top_text": clean_query.upper(),
        "bottom_text": "ЧИСТО Я В ЭТОТ МОМЕНТ",
        "emoji": "🔥",
        "is_ai": False
    }

