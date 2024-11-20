import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def generate_miniapp_keyboard():
    keyboard = InlineKeyboardMarkup()
    url = os.getenv('WEB_APP_URL')
    webAppInfo = WebAppInfo(url=url)
    button = InlineKeyboardButton(text="Открыть телеграм-приложение",
                                    web_app=webAppInfo)
    keyboard.add(button)
    return keyboard
