from aiogram.types import InlineKeyboardMarkup
from ..callback_data import event_type_data
from ..pref_keyboard import generate_events_pref_inline_keyboard


async def generate_events_types_markup(checked_types_codes: list[int],
                                       page: int, events_types: list[dict]) -> InlineKeyboardMarkup:
    return generate_events_pref_inline_keyboard(events_types,
                                                checked_types_codes,
                                                event_type_data,
                                                page)


