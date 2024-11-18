from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileStatesGroup(StatesGroup):
    show_profile = State()
    show_new_events = State()
    register_username = State()
    register_password = State()
    select_specific_page_new_events = State()
