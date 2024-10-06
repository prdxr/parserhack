import aiogram
import asyncio
import logging
import os

from loader import *
from database import user_preferences_collection
from utils.parser_api import get_updates
from utils.create_event_message import create_event_messsage
from models.User import User
from keyboards.inline.utils import *
from keyboards.inline.events_list_keyboard import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers.users.event_page_handler import get_event_page

CRAWLING_INTERVAL = os.getenv("API_CRAWLING_INTERVAL")
CRAWLING_INTERVAL = int(CRAWLING_INTERVAL) if CRAWLING_INTERVAL is not None else 5
logger = logging.getLogger(f"root.{__name__}")

PAGE_SIZE = 1
callback_data = CallbackData("page", "page_number")
storage = MemoryStorage()


async def send_new_events():
    while True:
        new_events = await get_updates()
        logger.info(f"{len(new_events)} new events received")

        async for user_preferences in user_preferences_collection.find({}):
            user = User.parse_obj(user_preferences)

            if user.agreed_to_mailing():
                user_events = []

                for new_event in new_events:
                    if user.agreed_to_accept_event(new_event):
                        event_message = create_event_messsage(new_event)
                        user_events.append(event_message)

                if user_events:
                    total_pages = math.ceil(len(user_events) / PAGE_SIZE)
                    current_page = 1

                    await storage.update_data(user.id, events=user_events, page_size=PAGE_SIZE,
                                              current_page=current_page)

                    paginated_events = user_events[:PAGE_SIZE]
                    message_text = "<b>Новые мероприятия:</b>\n\n" + "\n\n".join(paginated_events)

                    try:
                        message = await bot.send_message(user.id,
                                                         message_text,
                                                         parse_mode="HTML",
                                                         disable_web_page_preview=True,
                                                         reply_markup=get_events_list_keyboard(current_page,
                                                                                               PAGE_SIZE,
                                                                                               user_events))

                        await storage.update_data(user.id, last_events_list_message_id=message.message_id)

                    except aiogram.utils.exceptions.BotBlocked:
                        await user.delete()
                        break
        await asyncio.sleep(CRAWLING_INTERVAL)


@dp.callback_query_handler(text_contains="page:")
async def handle_page_change(query: types.CallbackQuery, state: FSMContext):
    await get_event_page(query, state)
