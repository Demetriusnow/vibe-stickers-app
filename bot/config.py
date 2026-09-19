"""
Configuration loader for Vibe Stickers application.
Loads environment variables from .env file.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных из .env файла
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TENOR_API_KEY: str = os.getenv("TENOR_API_KEY", "")
    WEBAPP_URL: str = os.getenv("WEBAPP_URL") or os.getenv("RENDER_EXTERNAL_URL") or "https://vibe-stickers-u59u.onrender.com"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").strip().lower() in ("true", "1", "yes")
    BASE_URL: str = os.getenv("BASE_URL") or os.getenv("RENDER_EXTERNAL_URL") or "https://vibe-stickers-u59u.onrender.com"
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "false").strip().lower() in ("true", "1", "yes")
    BASE_DIR: Path = BASE_DIR


config = Config()
