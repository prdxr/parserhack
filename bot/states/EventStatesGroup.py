from aiogram.dispatcher.filters.state import StatesGroup, State


class EventStatesGroup(StatesGroup):
    get_events = State()
    select_specific_event_page = State()
    field = State()
