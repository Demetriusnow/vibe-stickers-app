"""
VibeStickers - Main Entry Point
Запускает одновременно Telegram Bot (aiogram 3) и Web-сервер (aiohttp) для Telegram Mini App.
"""
import asyncio
import logging
import sys
from aiohttp import web

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


from bot.config import config
from bot.bot_instance import bot, dp
from api.server import setup_app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("VibeStickers")


async def main():
    logger.info("=== Запуск Vibe Stickers (Telegram Mini App + Bot) ===")
    logger.info(f"Режим DEV_MODE: {config.DEV_MODE}")
    logger.info(f"URL Mini App: {config.WEBAPP_URL}")
    logger.info(f"Сервер слушает: http://{config.HOST}:{config.PORT}")

    app = await setup_app(bot, dp)
    runner = web.AppRunner(app)
    await runner.setup()

    # Попытка привязки к порту с авто-подбором, если порт занят другой программой (например, 8080)
    ports_to_try = [config.PORT, 8000, 8088, 8085, 5000, 3000]
    # Удаляем дубликаты, сохраняя порядок
    unique_ports = []
    for p in ports_to_try:
        if p not in unique_ports:
            unique_ports.append(p)

    active_port = None
    for test_port in unique_ports:
        try:
            site = web.TCPSite(runner, config.HOST, test_port)
            await site.start()
            active_port = test_port
            break
        except (PermissionError, OSError) as e:
            logger.warning(f"⚠️ Порт {test_port} недоступен или занят другим приложением ({e}). Пробуем следующий...")

    if not active_port:
        logger.error("❌ Не удалось занять ни один из свободных портов.")
        return

    logger.info(f"🚀 Веб-сервер успешно запущен на http://{config.HOST}:{active_port}")

    # Проверяем, задан ли реальный токен бота
    if config.BOT_TOKEN and config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        logger.info("🤖 Запуск polling Telegram-бота...")
        try:
            bot_info = await bot.get_me()
            logger.info(f"Бот подключен: @{bot_info.username} ({bot_info.first_name})")
            await dp.start_polling(bot, handle_as_tasks=True)
        except Exception as e:
            logger.error(f"Ошибка при запуске polling бота: {e}")
            logger.warning("Веб-сервер продолжает работу. Для работы бота укажите валидный BOT_TOKEN в .env")
            # Держим сервер запущенным
            while True:
                await asyncio.sleep(3600)
    else:
        logger.warning("⚠️ BOT_TOKEN не указан или оставлен шаблонным в .env!")
        logger.warning(f"Веб-приложение доступно для локального тестирования в браузере: http://{config.HOST}:{active_port}")
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Приложение остановлено.")
