# 🔥 Vibe Stickers — AI Telegram Mini App & Sticker Generator

> Генератор вирусных анимированных и видео-мем стикеров в формате **Telegram Mini App (TMA)** с Tinder-механикой свайпов («Vibe Swiper») и моментальным добавлением в личный стикерпак.

---

## ⚡ Особенности проекта

- **Настоящее Telegram Mini App (TMA):**
  - Работает нативно внутри Telegram на iOS, Android и Desktop.
  - Автоматическая авторизация по `Telegram.WebApp.initData` (HMAC-SHA256) — никаких логинов и паролей.
  - Настоящая тактильная отдача смартфона (**Haptic Feedback**) при каждом свайпе и добавлении в пак.
  - Автоматическая подстройка под тему оформления Telegram пользователя.
  - Защита от случайного сворачивания шторки при свайпах (`disableVerticalSwipes`).
- **Tinder-механика (Vibe Swiper):**
  - Карточки с зацикленными видео/гифками и мемными панчлайнами.
  - Свайп вправо (или кнопка «🔥 В ПАК») — добавление стикера в Telegram-пак.
  - Свайп влево (или кнопка «❌ СКИП») — пропуск карточки.
  - Кнопки смены фона и редактирования текста на лету.
- **Zero-Waste Pipeline:**
  - На клиенте видео и текст отображаются **мгновенно (0 мс задержки)** через аппаратный CSS/GPU оверлей.
  - Тяжёлый рендеринг видео в FFmpeg запускается **только** для тех стикеров, которые пользователь действительно лайкнул.
- **Соблюдение стандартов Telegram Video Stickers:**
  - Контейнер WebM, кодек VP9 (`libvpx-vp9`).
  - Разрешение ровно 512×512, длительность до 2.95 сек, частота 30 FPS, без звука (`-an`).
  - Жесткий лимит размера файла: <= 256 КБ (в среднем 180–230 КБ).
- **Офлайн & Демо-режим:**
  - Приложение можно открывать и тестировать прямо в обычном браузере (Chrome, Edge, Firefox).
  - Если API-ключи Gemini или Tenor не заданы, активируется встроенный каталог готовых вайбов и мемных шаблонов.

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

Убедитесь, что установлен Python 3.10+ (в проекте используется встроенный автономный `imageio-ffmpeg`, системный FFmpeg устанавливать не требуется):

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполните ключи в `.env`:
- `BOT_TOKEN`: токен бота от [@BotFather](https://t.me/BotFather).
- `GEMINI_API_KEY`: бесплатный ключ от [Google AI Studio](https://aistudio.google.com/) (опционально, есть fallback).
- `TENOR_API_KEY`: ключ Tenor v2 от Google Cloud (опционально, есть fallback).
- `WEBAPP_URL`: URL вашего Mini App (по умолчанию `http://127.0.0.1:8080`).

---

## 📱 Подключение Mini App к Telegram (BotFather)

Чтобы приложение открывалось прямо внутри Telegram:

1. **Получите HTTPS-ссылку** для локального сервера (Telegram требует HTTPS):
   - Через Cloudflare Tunnel (бесплатно):
     ```bash
     cloudflared tunnel --url http://127.0.0.1:8080
     ```
   - Или через LocalTunnel:
     ```bash
     npx localtunnel --port 8080
     ```
   - Скопируйте полученный HTTPS адрес (например, `https://vibe-stickers-demo.loca.lt`) в переменную `WEBAPP_URL` в `.env`.

2. **Настройте кнопку Menu Button в BotFather**:
   - Откройте [@BotFather](https://t.me/BotFather) в Telegram.
   - Отправьте команду `/setmenubutton` -> выберите вашего бота.
   - Введите текст кнопки: `🔥 Vibe Stickers`.
   - Отправьте HTTPS-ссылку на ваше приложение.

3. **Запустите приложение**:
   ```bash
   python run.py
   ```

Теперь при открытии чата с ботом слева от поля ввода появится кнопка **«🔥 Vibe Stickers»**, открывающая приложение на весь экран!

---

## 📂 Структура проекта

```
vibe_stickers_app/
├── bot/                       # Telegram Бот (aiogram 3)
│   ├── config.py              # Конфигурация и переменные окружения
│   ├── bot_instance.py        # Инициализация Bot и Dispatcher
│   ├── sticker_manager.py     # Управление видео-стикерпаками пользователя
│   └── handlers.py            # Обработчики команд /start и /mypack
├── core/                      # Медиа-пайплайн и AI
│   ├── gemini_client.py       # Генерация фраз и тегов через Gemini Flash
│   ├── tenor_client.py        # Поиск видео-шаблонов через Tenor v2
│   └── video_processor.py     # Pillow PNG оверлей + FFmpeg VP9 конвертация
├── api/                       # REST API и веб-сервер (aiohttp)
│   ├── auth.py                # Валидация Telegram WebApp initData (HMAC-SHA256)
│   ├── routes.py              # Эндпоинты генерации, поиска и коммита стикеров
│   └── server.py              # Сервер aiohttp и раздача статики
├── webapp/                    # Нативное Telegram Mini App
│   ├── index.html             # Главный интерфейс
│   ├── css/style.css          # Стилизация и анимации Tinder-свайпера
│   └── js/
│       ├── telegram.js        # Интеграция с Telegram WebApp SDK & Haptics
│       ├── swiper.js          # Жестовый движок карточек
│       └── app.js             # Логика приложения и обмен с API
├── run.py                     # Единая точка запуска (Bot + WebApp)
└── requirements.txt           # Зависимости проекта
```
