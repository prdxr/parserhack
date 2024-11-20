from aiogram.utils.callback_data import CallbackData


event_type_data = CallbackData("event_type", "type_code", "page_number")
tag_data = CallbackData("event_tag", "type_code", "page_number")
event_list_data = CallbackData("event_list", "page_number")
mailing_type_data = CallbackData("mailing_type", "type")
mailing_status_data = CallbackData("mailing_status", "status")
action_button_data = CallbackData("action", "type")
select_page_data = CallbackData("select_page")
profile_show_preferences_data = CallbackData("show_preferences")
profile_mailing_status_data = CallbackData("toggle_mailing_status")
profile_mailing_type_data = CallbackData("toggle_mailing_all")
profile_notification_status_data = CallbackData("toggle_notification_status")
profile_select_events_data = CallbackData("select_events")
profile_select_tags_data = CallbackData("select_tags")