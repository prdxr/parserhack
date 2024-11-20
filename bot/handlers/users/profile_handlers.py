import math
import os
import re

import aiohttp
import requests
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from handlers.users.user import move_to_specific_page
from keyboards.inline import get_events_list_keyboard
from keyboards.inline.events_prefs import generate_events_types_markup, generate_tags_markup
from keyboards.inline.events_prefs.back_to_profile_keyboard import generate_back_to_profile_keyboard
from keyboards.inline.events_prefs.choose_events_or_tags import generate_preferences_choice_keyboards
from keyboards.inline.profile_keyboard import generate_profile_keyboard
from loader import dp, bot
from login import API_BASE_URL, get_token
from states.EventStatesGroup import EventStatesGroup
from states.PreferencesStatesGroup import PreferencesStatesGroup
from states.ProfileStatesGroup import ProfileStatesGroup
from utils import get_events_types, get_tags, create_events_response, get_indexes
from utils.create_events_response import create_new_events_response

token = get_token()
headers = {
    "Authorization": f"Token {token}"
}
pref_page_size = int(os.getenv("PREF_PAGE_SIZE"))
events_page_size = int(os.getenv("EVENTS_PAGE_SISE"))

async def __get_profile_text(user):
    event_types = await get_events_types()
    tag_types = await get_tags()

    event_type_dict = {event_type['type_code']: event_type['description'] for event_type in event_types}
    tag_dict = {tag['tag_code']: tag['description'] for tag in tag_types}

    printed_events = [event_type_dict.get(event_type_id) for event_type_id in user['event_preferences']]
    printed_tags = [tag_dict.get(tag_id) for tag_id in user['tag_preferences']]

    events_str = ', '.join(printed_events) if printed_events else 'Не выбрано'
    tags_str = ', '.join(printed_tags) if printed_tags else 'Не выбрано'
    profile_text = (
        f"👤 <b>Имя пользователя</b>: {user['username']}\n"
        f"📱 <b>Telegram ID</b>: <code>{user['telegram_id']}</code>\n"
        f"🎫 <b>Предпочтения мероприятий</b>: {events_str}\n"
        f"🏷️ <b>Предпочтения по тегам</b>: {tags_str}\n"
    )
    return profile_text



@dp.message_handler(state=ProfileStatesGroup.register_username)
async def register_username(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    if __check_credentials(message):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text="Неверный формат имени пользователя. Введите другое имя: ")
        except MessageNotModified:
            pass
        await message.delete()
        return
    response = requests.post(API_BASE_URL + "auth/users/", data={"username": message.text})
    response_json = response.json()
    if 'username' in response_json:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text="Имя пользователя занято. Введите другое имя: ")
        except MessageNotModified:
            await message.delete()
        await message.delete()
        return
    else:
        await state.update_data(username=message.text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Введите пароль: ")
        await state.set_state(ProfileStatesGroup.register_password)
        await message.delete()


@dp.message_handler(state=ProfileStatesGroup.register_password)
async def register_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    username = data["username"]
    password = message.text
    if __check_credentials(message):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text="Неверный формат пароля. Введите другой: ")
        except MessageNotModified:
            pass
        await message.delete()
        return
    data = {
        "username": username,
        "password": password,
        "telegram_id": message.from_user.id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=API_BASE_URL + "auth/users/", data=data) as response:
            if response.status == 400:
                try:
                    reply_message = await response.json()
                    password_errors = reply_message.get("password", [])
                    if password_errors:
                        error_text = "\n".join(password_errors)
                    else:
                        error_text = "Слишком слабый пароль. Введите снова"
                    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=error_text)
                    await message.delete()
                except MessageNotModified:
                    await message.delete()
                return
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Вы успешно зарегистрированы\n"
                                                                             "/profile - для просмотра профиля")
    await message.delete()
    await state.finish()



@dp.callback_query_handler(lambda c: c.data in ['toggle_mailing_all', 'toggle_mailing_status'],
                           state=ProfileStatesGroup.show_profile)
async def toggle_mailing_field(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data['tg_user']
    field_to_toggle = 'mailing_all' if query.data == 'toggle_mailing_all' else 'mailing_status'

    endpoint = 'toggle-mailing-all/' if query.data == 'toggle_mailing_all' else 'toggle-mailing-status/'
    response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/" + endpoint, headers=headers)
    if (response.status_code == 200):
        user[field_to_toggle] = not user[field_to_toggle]

        await state.update_data(tg_user=user)


        await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user), parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'toggle_notification_status', state=ProfileStatesGroup.show_profile)
async def toggle_notification_status(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data['tg_user']
    response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/toggle-notification-status/", headers=headers)
    if (response.status_code == 200):
        user['notification_status'] = not user['notification_status']
        await state.update_data(tg_user=user)
        await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user), parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'show_preferences', state=ProfileStatesGroup.show_profile)
async def start_pref_setting(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    await state.update_data(current_page=1)

    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                          text="Выберите желаемые настройки:", reply_markup=generate_preferences_choice_keyboards())
    await state.set_state(PreferencesStatesGroup.choose_events_or_tags)


@dp.callback_query_handler(lambda c: c.data == 'select_events', state=PreferencesStatesGroup.choose_events_or_tags)
async def select_events(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    user = data['tg_user']
    await state.update_data(current_page=1)
    events_types = await get_events_types()
    await state.update_data(events=events_types)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                          text="Выберите типы мероприятий: ",
                                reply_markup=await generate_events_types_markup(user['event_preferences'], 1, events_types))
    await state.set_state(PreferencesStatesGroup.events_types)


# Получаем новый тип мероприятия.
# Сохраняем его в машину состояний и изменяем разметку
@dp.callback_query_handler(text_contains="event_type",
                           state=PreferencesStatesGroup.events_types)
async def accept_event_type(query: types.CallbackQuery, state: FSMContext):
    callback_data = query.data
    button_data = callback_data.split(":")
    type_code = int(button_data[1])
    str_page_number = button_data[2]
    data = await state.get_data()
    user = data["tg_user"]
    if (str_page_number == '0'):
        await query.answer()
        return
    if str_page_number == '-1':
        response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/change-event-preference/",
                       json={"event_preferences": user['event_preferences']}, headers=headers)
        await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user), parse_mode='HTML')
        await state.set_state(ProfileStatesGroup.show_profile)
        return
    # Если передаем None, значит нажата кнопка с типом мероприятия
    if str_page_number == "None":
        try:
            user_prefs_set = set(user['event_preferences'])
            if type_code in user_prefs_set:
                user_prefs_set.remove(type_code)
            else:
                user_prefs_set.add(type_code)
            user['event_preferences'] = list(user_prefs_set)
            events_types = data['events']
            await state.update_data(tg_user=user)
            await query.message.edit_reply_markup(await generate_events_types_markup(user['event_preferences'],
                                                                     data["current_page"], events_types))
        except MessageNotModified:
            pass
        return

    page_number = int(str_page_number)

    events_type = data['events']
    await query.message. \
        edit_reply_markup(await generate_events_types_markup(user['event_preferences'],
                                                             page_number, events_type))
    await state.update_data(current_page=page_number)
    await PreferencesStatesGroup.events_types.set()

@dp.callback_query_handler(lambda c: c.data == 'select_tags', state=PreferencesStatesGroup.choose_events_or_tags)
async def select_tags(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    user = data['tg_user']
    tags = await get_tags()
    await state.update_data(events=tags)
    await state.update_data(current_page=1)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                text='Выберите теги мероприятий:',
                                reply_markup=await generate_tags_markup(user['tag_preferences'], 1, tags))
    await state.set_state(PreferencesStatesGroup.tags_types)



# Получаем и сохраняем новые теги
@dp.callback_query_handler(text_contains="event_tag", state=PreferencesStatesGroup.tags_types)
async def accept_tag(query: types.CallbackQuery, state: FSMContext):
    callback_data = query.data
    button_data = callback_data.split(":")
    tag_code = int(button_data[1])
    str_page_number = button_data[2]
    data = await state.get_data()
    user = data["tg_user"]
    if (str_page_number == '0'):
        await query.answer()
        return

    if str_page_number == '-1':
        response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/change-tag-preferences/",
                                  json={"tag_preferences": user['tag_preferences']}, headers=headers)
        await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user),
                                      parse_mode='HTML')
        await state.set_state(ProfileStatesGroup.show_profile)
        return

    if str_page_number == "None":
        user_tag_prefs_set = set(user['tag_preferences'])
        if tag_code in user_tag_prefs_set:
            user_tag_prefs_set.remove(tag_code)
        else:
            user_tag_prefs_set.add(tag_code)
        user['tag_preferences'] = list(user_tag_prefs_set)
        await state.update_data(tg_user=user)
        tags = data['events']
        await query.message.edit_reply_markup(await generate_tags_markup(user['tag_preferences'],
                                                                         data["current_page"], tags))
        return

    page_number = int(str_page_number)
    try:
        tags = data['events']
        await query.message.edit_reply_markup(await generate_tags_markup(user['tag_preferences'],
                                                                         page_number, tags))
    except MessageNotModified:
        pass
    await state.update_data(current_page=page_number)
    await PreferencesStatesGroup.tags_types.set()




@dp.callback_query_handler(lambda c: c.data == '/new_events', state=ProfileStatesGroup.show_profile)
async def show_new_events_from_profile(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data["tg_user"]
    await show_new_events(query, state, user)

@dp.callback_query_handler(lambda c: c.data == '/notification_events', state="*")
async def show_notification_events(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user_data = requests.get(API_BASE_URL + f"auth/users/all", headers=headers).json()
    user = None
    for u in user_data:
        if u['telegram_id'] == user_id:
            user = u
            break
    await state.update_data(tg_user=user)
    data = await state.get_data()
    user = data["tg_user"]
    await show_new_events(query, state, user)

@dp.callback_query_handler(text_contains="event_list", state=ProfileStatesGroup.show_new_events)
async def get_new_event_pages(query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.set_state(ProfileStatesGroup.show_new_events)
    query_data = query.data.split(":")
    str_page_number = query_data[1]
    new_page_number = int(str_page_number)
    # Завершаем просмотр мероприятий
    if int(new_page_number) == -1:
        data = await state.get_data()
        user = data['tg_user']
        events_to_delete = data.get("events_to_delete", [])
        data = {
            "remove": events_to_delete
        }
        response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/remove-new-events/",
                                  json=data, headers=headers)
        user['new_events'] = [event for event in user['new_events'] if event not in events_to_delete]
        await state.update_data(tg_user=user)
        await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user),
                                      parse_mode='HTML')

        await state.set_state(ProfileStatesGroup.show_profile)
        return
    await _handle_page_changing(query, state, new_page_number)

@dp.callback_query_handler(text_contains="select_page", state=ProfileStatesGroup.show_new_events)
async def get_new_event_pages(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    events_data = data.get("events", [])
    await state.set_state(ProfileStatesGroup.select_specific_page_new_events)
    await query.message.edit_text(text="Введите нужную страницу\n"
                                       "/back для возврата")
    await state.update_data(page_size=events_page_size)
    await state.update_data(events=events_data)
    await state.update_data(max_pages=math.ceil(len(events_data) / events_page_size))

@dp.message_handler(state=ProfileStatesGroup.select_specific_page_new_events)
async def get_specific_page_new_events(message: types.Message, state:FSMContext):
    await move_to_specific_page(message, state)

@dp.callback_query_handler(text_contains="select_page", state=PreferencesStatesGroup.events_types)
async def get_specific_page_events(query: types.CallbackQuery, state: FSMContext):
    current_type = 'events_type'
    await _select_specific_page_message(query, state, current_type)


@dp.callback_query_handler(text_contains="select_page", state=PreferencesStatesGroup.tags_types)
async def get_specific_page_tags(query: types.CallbackQuery, state: FSMContext):
    current_type = 'tags'
    await _select_specific_page_message(query, state, current_type)

async def _select_specific_page_message(query: types.CallbackQuery, state: FSMContext, current_type):
    data = await state.get_data()

    events_data = data.get("events", [])
    await state.set_state(PreferencesStatesGroup.select_specific_page_types)
    await query.message.edit_text(text="Введите нужную страницу\n"
                                       "/back для возврата")
    await state.update_data(current_type=current_type)
    await state.update_data(page_size=pref_page_size)
    await state.update_data(events=events_data)
    await state.update_data(max_pages=math.ceil(len(events_data) / pref_page_size))

@dp.message_handler(state=PreferencesStatesGroup.select_specific_page_types)
async def move_to_specific_page_types_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await _move_to_specific_page_types(message, state, data['current_type'])


async def _move_to_specific_page_types(message: types.Message, state: FSMContext, current_type):
    data = await state.get_data()
    message_id = data['registration_message_id']
    chat_id = data['registration_chat_id']
    tg_user = data['tg_user']
    if message.text == "/back":
        new_page_number = data.get("current_page", 1)
        if current_type == "events_type":
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=
                                                await generate_events_types_markup(tg_user['event_preferences'],
                                                                                   new_page_number, data['events']))
            await state.set_state(PreferencesStatesGroup.events_types)
        else:
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=
                                          await generate_tags_markup(tg_user['tag_preferences'],
                                                                             new_page_number, data['events']))
            await state.set_state(PreferencesStatesGroup.tags_types)
        await message.delete()
        return
    try:
        new_page_number = int(message.text)
        if (new_page_number < 1 or new_page_number > data.get("max_pages")):
            raise ValueError
        if current_type == 'events_type':
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await generate_events_types_markup(tg_user['event_preferences'], new_page_number, data['events']))
            await message.delete()
            await state.set_state(PreferencesStatesGroup.events_types)
        else:
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=await generate_tags_markup(tg_user['tag_preferences'],
                                                                                          new_page_number,
                                                                                          data['events']))
            await message.delete()
            await state.set_state(PreferencesStatesGroup.tags_types)
        await state.update_data(current_page=new_page_number)
    except ValueError:
        await message.delete()
        try:
            await bot.edit_message_text(text="Пожалуйста, введите корректный номер страницы (число).\n"
                                             "/back для возврата",
                                        chat_id=chat_id,
                                        message_id=message_id)
        except (MessageNotModified):
            pass


@dp.callback_query_handler(lambda c: c.data == '/menu', state=ProfileStatesGroup.show_profile)
async def back_to_menu(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text("Вы вышли в меню")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == '/profile', state=PreferencesStatesGroup.choose_events_or_tags)
async def back_to_profile(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data['tg_user']
    await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user), parse_mode='HTML')
    await state.set_state(ProfileStatesGroup.show_profile)

@dp.callback_query_handler(lambda c: c.data == '/profile', state=ProfileStatesGroup.show_new_events)
async def back_to_profile(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data['tg_user']
    try:
        data = await state.get_data()
        events_to_delete = data.get('events_to_delete')
        data = {
            "remove": events_to_delete
        }
        response = requests.patch(API_BASE_URL + f"auth/users/profile/{user['id']}/remove-new-events/",
                                  json=data, headers=headers)
        user['new_events'] = [event for event in user['new_events'] if event not in events_to_delete]
        await state.update_data(tg_user=user)
    except Exception:
        pass
    await query.message.edit_text(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user), parse_mode='HTML')
    await state.set_state(ProfileStatesGroup.show_profile)

async def show_new_events(query: types.CallbackQuery, state: FSMContext, user):
    response = requests.get(API_BASE_URL + f"auth/users/profile/{user['id']}/new-events/", headers=headers)
    new_events = response.json()
    await state.update_data(last_events_list_message_id=query.message.message_id)
    await state.update_data(events=new_events)
    await state.update_data(current_page=1)
    await state.update_data(page_size=events_page_size)
    await state.set_state(ProfileStatesGroup.show_new_events)
    if len(new_events) == 0:
        result_message = "Не удалось найти мероприятия"
        await query.message.edit_text(result_message, reply_markup=generate_back_to_profile_keyboard())
    elif len(new_events) <= events_page_size:
        result_message = await create_new_events_response(0, len(new_events) - 1,
                                                new_events,state)
        await query.message.edit_text(result_message,
                                      disable_web_page_preview=True, reply_markup=generate_back_to_profile_keyboard())
    else:
        result_message = await create_new_events_response(0, events_page_size - 1, new_events, state)
        await query.message.edit_text(result_message,
                                      parse_mode="HTML",
                                      disable_web_page_preview=True,
                                      reply_markup=get_events_list_keyboard(1,
                                                                            events_page_size,
                                                                            new_events))

async def _handle_event_pref_page_changing(query, state: FSMContext, new_page_number: int):
    data = await state.get_data()
    if "current_page" not in data:
        await query.message.delete()
        await state.finish()
        return

    await state.update_data(current_page=new_page_number)

    data = await state.get_data()
    events = data.get("events", [])
    page_size = data["page_size"]
    start_index, end_index = get_indexes(events, new_page_number, page_size)
    new_message_text = create_events_response(start_index, end_index, events)

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


async def _handle_page_changing(query, state: FSMContext, new_page_number: int):
    data = await state.get_data()

    if "current_page" not in data:
        await query.message.delete()
        await state.finish()
        return
    tg_user = data['tg_user']
    await state.set_state(ProfileStatesGroup.show_new_events)
    await state.update_data(current_page=new_page_number)

    data = await state.get_data()
    events = data.get("events", [])
    page_size = data["page_size"]
    start_index, end_index = get_indexes(events, new_page_number, page_size)
    new_message_text = await create_new_events_response(start_index, end_index, events, state)

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

def __check_credentials(message: types.Message):
    allowed_pattern = re.compile(r'^[A-Za-z0-9!@#$%^&*(),.?":{}|<>_\-+=/\\`~\[\];\']+$')
    text = message.text
    if text.startswith('/') or allowed_pattern.search(text):
        return False
    return True
