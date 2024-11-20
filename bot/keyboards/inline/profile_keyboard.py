from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import profile_mailing_status_data, profile_show_preferences_data, profile_mailing_type_data, \
    profile_notification_status_data


def generate_profile_keyboard(user):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='🗳️ Указать предпочтения', callback_data=profile_show_preferences_data.new()))
    mailing_type_text = '📨 Тип рассылки: ' + ('Все 📢' if user['mailing_all'] else 'По предпочтениям 🎯')
    mailing_status_text = '📮 Включить рассылку: ' + ('✅ ' if user['mailing_status'] else '❌ ')
    notification_status_text = '🔔 Включить уведомления: ' + ('✅ ' if user['notification_status'] else '❌ ')
    keyboard.add(InlineKeyboardButton(text=mailing_type_text, callback_data=profile_mailing_type_data.new()))
    keyboard.add(InlineKeyboardButton(text=mailing_status_text, callback_data=profile_mailing_status_data.new()))
    keyboard.add(InlineKeyboardButton(text=notification_status_text, callback_data=profile_notification_status_data.new()))
    keyboard.add(InlineKeyboardButton(text=f'📩 Новые события +{len(user["new_events"])}', callback_data='/new_events'))
    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='/menu'))
    return keyboard