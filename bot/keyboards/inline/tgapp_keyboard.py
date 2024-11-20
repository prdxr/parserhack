import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_miniapp_keyboard():
    keyboard = InlineKeyboardMarkup(InlineKeyboardButton(text="Открыть телеграм-приложение"),
                                    web_app=os.getenv('WEB_APP_URL'))
    return keyboard