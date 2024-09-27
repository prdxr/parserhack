import os
import sys
import time
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from login import get_token
import logging.config
from pathlib import Path


BASE_DIR = Path(__file__).parent.resolve()


# Создаем папки для логов
log_err_dir = BASE_DIR / "logs" / "err"
log_out_dir = BASE_DIR / "logs" / "out"

log_err_dir.mkdir(parents=True, exist_ok=True)
log_out_dir.mkdir(parents=True, exist_ok=True)

# Конфигурация логгера
logging.config.fileConfig(
    BASE_DIR / "logging.conf",
    defaults={
        "err_log_file": (log_err_dir / "err.log").as_posix(),
        "out_log_file": (log_out_dir / "out.log").as_posix()
    },
    disable_existing_loggers=False
)

logger = logging.getLogger(f"root.{__name__}")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("Can't find BOT_TOKEN env variable")
    sys.exit()
    
bot = Bot(BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

ADMINS_IDS = os.getenv("ADMINS_IDS")
admins = []
if ADMINS_IDS is not None:    
    admins = ADMINS_IDS.split(",")
    admins = [admin for admin in admins if admin != ""]

django_start = False

while django_start is False:
    try:
        token = get_token()
        django_start = True
    except Exception:
        time.sleep(3)
