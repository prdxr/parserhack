from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import MessageToDeleteNotFound
from loader import dp, bot


@dp.callback_query_handler(text_contains="action", state="*")
async def cancel_action(query: types.CallbackQuery, state: FSMContext):
    query_data = query.data.split(":")
    action_type = query_data[1]
    if action_type == "cancel":
        try:
            data = await state.get_data()
            blocking_message_id = data["blocking_message_id"]
            await bot.delete_message(query.from_user.id, 
                                     blocking_message_id)
        except (MessageToDeleteNotFound, KeyError):
            pass
        await query.message.delete()
        await state.finish()


@dp.message_handler(Command('cancel'), state="*")
async def cancel_action(message: types.Message, state: FSMContext):
    await message.answer("Действие отменено")
    await message.delete()
    await state.finish()
