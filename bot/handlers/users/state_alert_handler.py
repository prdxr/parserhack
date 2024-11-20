
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from handlers.users.handlers_utils import cancel_message_exists
from handlers.users.profile_handlers import __get_profile_text
from keyboards.default.events_menu import events_menu
from keyboards.inline import cancel_action_keyboard
from keyboards.inline.tgapp_keyboard import generate_miniapp_keyboard
from keyboards.inline.profile_keyboard import generate_profile_keyboard
from loader import dp
from login import get_token, API_BASE_URL
from states.ProfileStatesGroup import ProfileStatesGroup

token = get_token()
headers = {
    "Authorization": f"Token {token}"
}

@dp.message_handler(Command(commands=['start', 'events', 'profile']), state="*")
async def handle_commands(message: types.Message, state: FSMContext):
    command = message.get_command()
    current_state = await state.get_state()
    if current_state:
        await state.finish()

    if command == '/start':
        await message.answer("Добро пожаловать!\nВыберите команду /events"
                             " для начала работы с мероприятиями.\nКоманда /profile"
                             " позволит вам создать зарегистрироваться и выбрать категории интересующих вас мероприятий."
                             "\nТакже в профиле можно настроить рассылку новых мероприятий.", reply_markup=generate_miniapp_keyboard())

    elif command == '/events':
        await message.answer("Выберите интересующий способ получения мероприятий",
                                 reply_markup=events_menu)
    elif command == '/profile':
        await show_profile(message, state)


@dp.message_handler(state="*")
async def state_alert(message: types.Message, state: FSMContext):
    text = message.text
    current_state = await state.get_state()
    state_data = await state.get_data()
    if not cancel_message_exists(state_data) and current_state != None:
        new_message = await message.answer("Сначала необходимо завершить предыдущее действие!",
                                           reply_markup=cancel_action_keyboard)
        await state.update_data(existing_cancel_message_id=new_message.message_id)
    await message.delete()


async def show_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = requests.get(API_BASE_URL + f"auth/users/all", headers=headers).json()
    user = None
    for u in user_data:
        if u['telegram_id'] == user_id:
            user = u
            break
    if user is None:
        bot_message = await message.answer(text="Вы не зарегистрированы. Введите логин: ")
        await message.delete()
        await state.set_state(ProfileStatesGroup.register_username)
        await state.update_data(registration_message_id=bot_message.message_id,
                                registration_chat_id=bot_message.chat.id)
        return
    bot_message = await message.answer(await __get_profile_text(user), reply_markup=generate_profile_keyboard(user),
                                       parse_mode='HTML')
    await state.set_state(ProfileStatesGroup.show_profile)
    await state.update_data(tg_user=user)
    await state.update_data(registration_message_id=bot_message.message_id, registration_chat_id=bot_message.chat.id)
