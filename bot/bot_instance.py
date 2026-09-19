"""
Aiogram 3 Bot and Dispatcher initialization.
"""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.config import config
from bot.handlers import router as base_router

# Валидация формата токена для безопасного импорта в dev-режиме
token = config.BOT_TOKEN.strip() if config.BOT_TOKEN else ""
if not token or ":" not in token or token == "YOUR_BOT_TOKEN_HERE":
    # Шаблонный токен для предотвращения TokenValidationError при локальной разработке
    token = "1234567890:AAFakeTokenForLocalDevTestingOnly12345"

bot = Bot(
    token=token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.include_router(base_router)
