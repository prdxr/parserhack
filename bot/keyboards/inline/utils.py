import math
from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline import select_page_data


def add_control_buttons(inline_keyboard: list[list[InlineKeyboardButton]],
                        objects: list, 
                        data: CallbackData, 
                        data_params: dict,
                        page_size: int,
                        current_page: int) -> None:
    """
    Добавляет к переданной inline_keyboard кнопки перехода по страницам
    """
    pages_count = math.ceil(len(objects) / page_size)

    if (current_page > 1):
        prev_button = InlineKeyboardButton(
            text="<<",
            callback_data=data.new(**data_params, page_number=current_page-1)
        )
    else:
        prev_button = InlineKeyboardButton(
            text="<<",
            callback_data=data.new(**data_params, page_number=0)
        )

    pages_display = InlineKeyboardButton(text=f"{current_page}/{pages_count}",
                                         callback_data=select_page_data.new())
    if (current_page < pages_count):
        next_button = InlineKeyboardButton(
            text=">>",
            callback_data=data.new(**data_params, page_number=current_page+1)
        )
    else:
        next_button = InlineKeyboardButton(
            text=">>",
            callback_data=data.new(**data_params, page_number=0)
        )
    cancel_button = InlineKeyboardButton(text="Готово", callback_data=data.new(**data_params, page_number=-1))
    inline_keyboard.append([prev_button, pages_display, next_button])
    inline_keyboard.append([cancel_button])



