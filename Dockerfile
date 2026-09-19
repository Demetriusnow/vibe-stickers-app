# ==============================================================================
# Dockerfile for Vibe Stickers (Telegram Mini App & Sticker Generator)
# Оптимизирован для деплоя на Render.com (Free Tier)
# ==============================================================================

FROM python:3.11-slim

# Установка системных утилит, FFmpeg и шрифтов с поддержкой кириллицы для Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-liberation \
    fonts-dejavu-core \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория приложения
WORKDIR /app

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Создание директории для пользовательских загрузок
RUN mkdir -p webapp/media/uploads

# Настройка переменных окружения по умолчанию
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Порт сервиса
EXPOSE 8080

# Запуск приложения (Telegram Бот + WebApp Сервер)
CMD ["python", "run.py"]
