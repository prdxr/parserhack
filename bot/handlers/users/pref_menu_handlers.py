from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from states.PreferencesStatesGroup import PreferencesStatesGroup
from keyboards.inline.events_prefs. \
    events_types_keyboard import generate_events_types_markup
from keyboards.inline.events_prefs.tags_keyboard import generate_tags_markup
from utils.database import user_preferences_collection


@dp.message_handler(Command("preferences"))
async def start_pref_setting(message: types.Message, state: FSMContext):
    # Загружаем уже существующие предпочтения пользователя
    user_preferences = await user_preferences_collection. \
        find_one({"_id": message.from_user.id})
    if user_preferences is not None:
        await state.update_data(events_types=user_preferences["events_types"])
        await state.update_data(tags=user_preferences["tags"])

    await state.update_data(current_page=1)
    data = await state.get_data()
    if "events_types" not in data.keys():
        await state.update_data(events_types=[])

    if "tags" not in data.keys():
        await state.update_data(tags=[])

    data = await state.get_data()
    await message.answer("Выберите интересующие вас виды мероприятий:",
                         reply_markup=await generate_events_types_markup(data["events_types"], 
                                                                          data["current_page"]))

    # Перенаправляем на хендлер-обработчик ответа
    await PreferencesStatesGroup.events_types.set()


# Получаем новый тип мероприятия.
# Сохраняем его в машину состояний и изменяем разметку
@dp.callback_query_handler(text_contains="event_type",
                           state=PreferencesStatesGroup.events_types)
async def accept_event_type(query: types.CallbackQuery, state: FSMContext):
    callback_data = query.data
    button_data = callback_data.split(":")
    type_code = int(button_data[1])
    button_type = button_data[2]
    data = await state.get_data()

    if button_type == "back":
        new_page = data.get("current_page") - 1
        await query.message.\
            edit_reply_markup(await generate_events_types_markup(data.get("events_types"),
                                                                 new_page))
        await state.update_data(current_page=new_page)
        await PreferencesStatesGroup.events_types.set()
    elif button_type == "next":
        new_page = data.get("current_page") + 1
        await query.message.\
            edit_reply_markup(await generate_events_types_markup(data.get("events_types"),
                                                                 new_page))
        await state.update_data(current_page=new_page)
        await PreferencesStatesGroup.events_types.set()
    elif button_type == "done":
        async with state.proxy() as data:
            # Сброс номера страницы для следующего выбора
            data["current_page"] = 1
            chat_id = query.from_user.id
            await query.message.delete()

            # Отправляем сообщение с выбором тегов
            await bot.send_message(chat_id=chat_id,
                text="Выберите теги для фильтрации интересующих мероприятий:",
                reply_markup=await generate_tags_markup(data["tags"], data["current_page"]))

        await PreferencesStatesGroup.tags.set()
    else:
        async with state.proxy() as data:
            events_types = add_code(data["events_types"], type_code)
            data["events_types"] = events_types

        await query.message.\
            edit_reply_markup(await generate_events_types_markup(data["events_types"],
                                                                 data["current_page"]))


# Получаем и сохраняем новые теги
@dp.callback_query_handler(text_contains="event_tag", state=PreferencesStatesGroup.tags)
async def accept_tag(query: types.CallbackQuery, state: FSMContext):
    callback_data = query.data
    button_data = callback_data.split(":")
    tag_code = int(button_data[1])
    button_type = button_data[2]
    data = await state.get_data()

    if button_type == "back":
        new_page = data.get("current_page") - 1
        await query.message.edit_reply_markup(await generate_tags_markup(data.get("tags"),
            new_page))
        await state.update_data(current_page=new_page)
        await PreferencesStatesGroup.tags.set()
    elif button_type == "next":
        new_page = data.get("current_page") + 1
        await query.message.edit_reply_markup(await generate_tags_markup(data.get("tags"),
            new_page))
        await state.update_data(current_page=new_page)
        await PreferencesStatesGroup.tags.set()
    elif button_type == "done":
        async with state.proxy() as data:
            tags = data.get("tags")
            events_types = data["events_types"]
            user_id = query.from_user.id
            creation_data = {
                "_id": user_id,
                "events_types": events_types,
                "tags": tags
            }
            update_data = {
                "events_types": events_types,
                "tags": tags
            }

            # Сохранить предпочтения пользователя
            user_preferences = await user_preferences_collection.find_one({"_id": user_id})

            if user_preferences is not None:
                await user_preferences_collection.update_one(
                    {"_id": user_id},
                    {"$set": update_data})
            else:
                await user_preferences_collection.insert_one(creation_data)

            await query.message.delete()
            await bot.send_message(chat_id=user_id, text="Настройки успешно сохранены")
        # Очистка состояния. Можно ли хранить предпочтения всегда в машине состояний?
        await state.finish()
    else:
        async with state.proxy() as data:
            tags = add_code(data["tags"], tag_code)
            data["tags"] = tags

        await query.message.edit_reply_markup(await generate_tags_markup(data["tags"],
            data["current_page"]))


def add_code(already_exists_codes: list[int], code: int) -> list[int]:
    if type(already_exists_codes) is not list:
        already_exists_codes = []

    # Если тип мероприятия уже есть в списке, значит удаляем
    if code in already_exists_codes:
        already_exists_codes.remove(code)
    else:
        already_exists_codes.append(code)

    return already_exists_codes