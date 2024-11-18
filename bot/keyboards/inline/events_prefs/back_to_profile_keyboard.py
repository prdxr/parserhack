from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def generate_back_to_profile_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='/profile'))
    return keyboard