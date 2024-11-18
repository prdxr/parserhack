from aiogram.dispatcher.filters.state import StatesGroup, State


class PreferencesStatesGroup(StatesGroup):
    choose_events_or_tags = State()
    events_types = State()
    tags_types = State()
    select_specific_page_types = State()