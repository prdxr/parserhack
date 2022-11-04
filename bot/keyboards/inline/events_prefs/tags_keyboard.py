from aiogram.types import InlineKeyboardMarkup
from ..callback_data import tag_data
from ..pref_inline_keyboard import generate_events_pref_inline_keyboard
from typing import List
from utils.parser_api import get_tags


def generate_tags_markup(checked_tags_codes: List[int],
                               page: int) -> InlineKeyboardMarkup:
    tags = await get_tags()
    return generate_events_pref_inline_keyboard(tags,
                                  checked_tags_codes,
                                  tag_data, page)
