from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import profile_select_events_data, profile_select_tags_data


def generate_preferences_choice_keyboards():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton(text='По типу события', callback_data=profile_select_events_data.new()))
    keyboard.add(InlineKeyboardButton(text='По тегам', callback_data=profile_select_tags_data.new()))
    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='/profile'))
    return keyboard