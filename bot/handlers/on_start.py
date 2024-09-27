import asyncio
from bot.jobs import send_new_events
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot.loader import bot
from .admin import send_to_admin


async def start(dp):
    await asyncio.create_task(send_new_events())  # периодическая задача для новых мероприятий
    await bot.set_my_commands(
        commands=[
            BotCommand("events", "Открыть меню мероприятий"),
            BotCommand("preferences", "Настроить интересы"),
            BotCommand("mailing", "Настройка рассылки мероприятий")
        ],
        scope=BotCommandScopeDefault()
    )
    await send_to_admin(dp)
