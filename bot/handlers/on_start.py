from aiogram.types import BotCommand, BotCommandScopeDefault
from loader import bot
from .admin import send_to_admin


async def start(dp):
    #asyncio.create_task(send_new_events())  # периодическая задача для новых мероприятий
    await bot.set_my_commands(
        commands=[
            BotCommand("events", "Открыть меню мероприятий"),
            BotCommand("profile", "Посмотреть профиль"),
            BotCommand("cancel", "Отменить действие и выйти в меню"),
        ],
        scope=BotCommandScopeDefault()
    )
    await send_to_admin(dp)
