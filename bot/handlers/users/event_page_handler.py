from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.create_events_response import create_events_response
from utils.get_indexes import get_indexes
from keyboards.inline.events_list_keyboard import get_events_list_keyboard


async def get_event_page(query: types.CallbackQuery, state: FSMContext):
    query_data = query.data.split(":")
    str_page_number = query_data[1]

    # Завершаем просмотр мероприятий
    if int(str_page_number) == -1:
        await query.message.delete()
        await state.finish()
        return

    data = await state.get_data()

    if "current_page" not in data:
        await query.message.delete()
        return

    current_page_number = data["current_page"]
    new_page_number = int(str_page_number)

    if new_page_number != current_page_number:
        await state.update_data(current_page=new_page_number)

        data = await state.get_data()
        events = data["events"]
        page_size = data["page_size"]
        start_index, end_index = get_indexes(events, new_page_number, page_size)
        new_message_text = create_events_response(start_index, end_index, events)

        await query.message.edit_text(text=new_message_text,
                                      disable_web_page_preview=True,
                                      reply_markup=get_events_list_keyboard(new_page_number,
                                                                            page_size,
                                                                            events))