import math

import requests

from login import get_token
from states.ProfileStatesGroup import ProfileStatesGroup
from utils import *
from models import *
from keyboards.inline import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified, MessageToEditNotFound
from loader import dp, bot
from states.EventStatesGroup import EventStatesGroup
from utils.create_events_response import create_new_events_response

PAGE_SIZE = os.getenv("EVENTS_PAGE_SISE")
PAGE_SIZE = int(PAGE_SIZE) if PAGE_SIZE is not None else 5
API_BASE_URL = os.getenv("API_BASE_URL")
headers = {
    'Authorization': f'Token {get_token()}'
}



@dp.message_handler(lambda message: message.text and message.text\
    in ["Все события", "Интересующие события"], state="*")
async def get_all_events(message: types.Message, state: FSMContext):
    events: list[dict] = []
    data = await state.get_data()
    # Если сообщение с виджетом перехода по страницам уже существует, 
    # то его нужно удалить для избежания конфликтов
    # с потенциально разным количеством мероприятий
    if "last_events_list_message_id" in data:
        try:
            await bot.delete_message(message.from_user.id, 
                                     data["last_events_list_message_id"])
        except MessageToDeleteNotFound:
            pass
    await state.finish()
    if message.text == "Все события":
        events.extend(await get_events())
    elif message.text == "Интересующие события":
        response = requests.get(f"{API_BASE_URL}auth/users/all", headers=headers).json()
        bot_user = None
        for user in response:
            if user['telegram_id'] == message.from_user.id:
                bot_user = user
                if len(user['event_preferences']) == 0 and len(user['tag_preferences']) == 0:
                    await bot.send_message(message.from_user.id,
                                        text="Вы не указали предпочтения в профиле\n"\
                                            "Воспользуйтесь командой /profile.")
                    return
                else:
                    events.extend(await get_events_by_preferences(user['event_preferences'],
                                                                  user['tag_preferences']))
                    break
        if bot_user is None:
            await bot.send_message(message.from_user.id,text="Вы не создали профиль.\n"\
                                    "Воспользуйтесь командой /profile.")
            return
    await state.set_state(EventStatesGroup.get_events)
    await state.update_data(events=events)
    await state.update_data(page_size=PAGE_SIZE)
    await state.update_data(current_page=1)

    user_id = message.from_user.id
    await message.delete()
    data = await state.get_data()
    events = data.get("events", [])
    page_size = int(data["page_size"])

    if len(events) == 0:
        result_message = "Не удалось найти мероприятия"
        await bot.send_message(user_id, result_message)
    elif len(events) <= page_size:
        result_message = create_events_response(0, len(events) - 1,
                                                events)
        await bot.send_message(user_id, result_message, 
                               disable_web_page_preview=True)
        await state.finish()
    else:
        result_message = create_events_response(0, page_size-1, events)
        message = await bot.send_message(user_id,
                                         result_message,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True,
                                         reply_markup=get_events_list_keyboard(1,
                                                                               page_size,
                                                                               events))
        # Для отслеживания последнего сообщения с виджетом переключения страниц
        await state.update_data(last_events_list_message_id=message.message_id)

@dp.callback_query_handler(text_contains="select_page", state=EventStatesGroup.get_events)
async def get_specific_page(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    events_data = data.get("events", [])
    await state.set_state(EventStatesGroup.select_specific_event_page)
    await query.message.edit_text(text="Введите нужную страницу\n"
                                       "/back для возврата")
    await state.update_data(events=events_data)
    await state.update_data(max_pages=math.ceil(len(events_data) / PAGE_SIZE))

@dp.message_handler(lambda message: message.text, state=EventStatesGroup.select_specific_event_page)
async def move_to_specific_page_handler(message: types.Message, state: FSMContext):
    await move_to_specific_page(message, state)


@dp.callback_query_handler(text_contains="event_list" , state=EventStatesGroup.get_events)
async def get_event_page_handler(query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.set_state(EventStatesGroup.get_events)
    query_data = query.data.split(":")
    str_page_number = query_data[1]
    new_page_number = int(str_page_number)
    if new_page_number == 0:
        await query.answer()
        return
    # Завершаем просмотр мероприятий
    if int(new_page_number) == -1:
        await query.message.delete()
        await query.answer("Просмотр мероприятий завершён")
        await state.finish()
        return
    await _handle_page_changing(query, state, new_page_number)


@dp.message_handler(lambda message: message.text and message.text\
    in ["По названию", "По адресу"], state="*")
async def send_name_request(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "last_events_list_message_id" in data:
        try:
            await bot.delete_message(message.from_user.id, 
                                     data["last_events_list_message_id"])
        except MessageToDeleteNotFound:
            pass
    await state.finish()
    if message.text == "По названию":
        await message.answer("Введите название интересующего мероприятия")
    else:
        await message.answer("Введите адрес или его часть")
    await state.update_data(type=message.text)
    await EventStatesGroup.field.set()


@dp.message_handler(state=EventStatesGroup.field)
async def get_events_by_name(message: types.Message, state: FSMContext):
    field = message.text.lower()
    data = await state.get_data()
    type = data["type"]
    events = await get_events()
    result_events: list[dict] = []
    
    for event in events:
        parsed_event = Event.parse_obj(event)
        if type == "По названию":
            if field in parsed_event.title.lower():
                result_events.append(event)
        else:
            if parsed_event.address is not None and \
                field in parsed_event.address.lower():
                    result_events.append(event)
    
    if len(result_events) == 0:
        result_message = "Не удалось найти мероприятия"
        await bot.send_message(message.from_user.id, result_message)
    elif len(result_events) <= PAGE_SIZE:
        result_message = create_events_response(0, len(result_events) - 1, 
                                                result_events)
        await bot.send_message(message.from_user.id, result_message, 
                               disable_web_page_preview=True)
        await state.finish()
        return
    else:
        await state.update_data(events=result_events)
        await state.update_data(page_size=PAGE_SIZE)
        await state.update_data(current_page=1)
        result_message = create_events_response(0, PAGE_SIZE-1, result_events)
        message = await bot.send_message(message.from_user.id,
                                         result_message,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True,
                                         reply_markup=get_events_list_keyboard(1, PAGE_SIZE,
                                                                               result_events))
        # Для отслеживания последнего сообщения с виджетом переключения страниц
        await state.update_data(last_events_list_message_id=message.message_id)
    await state.set_state(EventStatesGroup.get_events)



async def move_to_specific_page(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "/back":
        new_page_number = data.get("current_page", 1)
        await _handle_page_changing(message, state, new_page_number)
        return
    try:
        new_page_number = int(message.text)
        if (new_page_number < 1 or new_page_number > data.get("max_pages")):
            raise ValueError
        print("debug")
        await _handle_page_changing(message, state, new_page_number)
    except ValueError:
        await message.delete()
        try:
            await bot.edit_message_text(text="Пожалуйста, введите корректный номер страницы (число).\n"
                                             "/back для возврата",
                                        chat_id=message.from_user.id,
                                        message_id=data.get("last_events_list_message_id"))
        except (MessageNotModified):
            pass

async def _handle_page_changing(query, state: FSMContext, new_page_number: int):
    data = await state.get_data()

    if "current_page" not in data:
        await query.message.delete()
        await state.finish()
        return
    try:
        tg_user = data['tg_user']
        await state.set_state(ProfileStatesGroup.show_new_events)
    except Exception:
        await state.set_state(EventStatesGroup.get_events)
    await state.update_data(current_page=new_page_number)

    data = await state.get_data()
    events = data.get("events", [])
    page_size = data["page_size"]
    start_index, end_index = get_indexes(events, new_page_number, page_size)
    new_message_text = create_events_response(start_index, end_index, events) if await state.get_state() == EventStatesGroup.get_events.state\
        else await create_new_events_response(start_index, end_index, events, state)

    if (type(query) == types.Message):
        user_id = query.from_user.id
        message_id = data.get("last_events_list_message_id")
        await query.delete()
        try:
            await bot.edit_message_text(chat_id=user_id,
                message_id=message_id,
                text=new_message_text,
                disable_web_page_preview=True,
                reply_markup=get_events_list_keyboard(new_page_number, page_size, events))
        except MessageNotModified:
            pass
    else:
        try:
            await query.message.edit_text(text=new_message_text,
                                      disable_web_page_preview=True,
                                      reply_markup=get_events_list_keyboard(new_page_number,
                                                                            page_size,
                                                                            events))
        except MessageNotModified:
            pass

