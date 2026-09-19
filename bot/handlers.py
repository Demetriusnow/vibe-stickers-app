"""
Aiogram 3 command handlers: /start, /mypack, /help.
Configures MenuButtonWebApp and inline buttons for Telegram Mini App.
"""
import logging
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
)
from aiogram.exceptions import TelegramBadRequest

from bot.config import config
from bot.sticker_manager import get_pack_name, get_bot_username

logger = logging.getLogger(__name__)
router = Router(name="base_handlers")


def get_webapp_keyboard() -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопку запуска Mini App."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Открыть Vibe Stickers",
                    web_app=WebAppInfo(url=config.WEBAPP_URL)
                )
            ]
        ]
    )


@router.message(CommandStart())
async def handle_start(message: Message, bot: Bot):
    """
    Обработчик команды /start:
    - Настраивает нативную кнопку меню чата (MenuButtonWebApp).
    - Отправляет приветствие и инлайн-кнопку запуска Mini App.
    """
    user_name = message.from_user.first_name if message.from_user else "друг"
    
    # Настраиваем постоянную кнопку Mini App слева от поля ввода (Menu Button)
    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text="🔥 Vibe Stickers",
                web_app=WebAppInfo(url=config.WEBAPP_URL)
            )
        )
    except Exception as e:
        logger.warning(f"Не удалось установить MenuButtonWebApp для чата {message.chat.id}: {e}")

    text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        "⚡ <b>Vibe Stickers</b> — это генератор вирусных видео-стикеров с механикой свайпов!\n\n"
        "👉 Свайпай вправо (или жми 🔥), чтобы мгновенно добавить мем-стикер в свой персональный пак в Telegram.\n"
        "👉 Свайпай влево, чтобы пропустить.\n"
        "👉 Меняй текст и фоны прямо на лету!\n\n"
        "Нажми кнопку ниже, чтобы начать генерировать вайбы 👇"
    )

    await message.answer(text, reply_markup=get_webapp_keyboard())


@router.message(Command("mypack"))
async def handle_mypack(message: Message, bot: Bot):
    """
    Обработчик команды /mypack:
    Проверяет наличие стикерпака пользователя и отправляет ссылку на него.
    """
    if not message.from_user:
        await message.answer("Ошибка определения пользователя.")
        return

    user_id = message.from_user.id
    bot_username = await get_bot_username(bot)
    pack_name = get_pack_name(user_id, bot_username)
    pack_link = f"https://t.me/addstickers/{pack_name}"

    try:
        sticker_set = await bot.get_sticker_set(name=pack_name)
        count = len(sticker_set.stickers)
        text = (
            f"📁 <b>Твой персональный стикерпак:</b>\n\n"
            f"🏷 Название: <code>{sticker_set.title}</code>\n"
            f"📊 Количество стикеров: <b>{count} / 120</b>\n"
            f"🔗 Прямая ссылка: <a href=\"{pack_link}\">{pack_link}</a>"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📥 Добавить пак себе", url=pack_link)
                ],
                [
                    InlineKeyboardButton(
                        text="⚡ Добавить новые стикеры",
                        web_app=WebAppInfo(url=config.WEBAPP_URL)
                    )
                ]
            ]
        )
        await message.answer(text, reply_markup=keyboard, disable_web_page_preview=False)
    except TelegramBadRequest as e:
        if "STICKERSET_INVALID" in str(e):
            text = (
                "У тебя пока ещё нет созданного стикерпака! 🧩\n\n"
                "Открой приложение, выбери понравившийся мем и свайпни вправо — твой личный пак создастся автоматически!"
            )
            await message.answer(text, reply_markup=get_webapp_keyboard())
        else:
            logger.error(f"Ошибка проверки стикерпака для {user_id}: {e}")
            await message.answer("Произошла ошибка при проверке стикерпака. Попробуй позже.")


@router.message(Command("help"))
async def handle_help(message: Message):
    """Справочная информация."""
    text = (
        "ℹ️ <b>Как пользоваться Vibe Stickers:</b>\n\n"
        "1. Запусти Mini App кнопкой внизу или командой /start.\n"
        "2. Листай карточки: вправо — сохранить в пак, влево — пропустить.\n"
        "3. Используй команду /mypack в любой момент, чтобы получить ссылку на свой стикерпак в Telegram."
    )
    await message.answer(text, reply_markup=get_webapp_keyboard())
