import os

import requests
from aiogram.dispatcher import FSMContext

from login import get_token
from utils.create_event_message import create_event_messsage

API_BASE_URL = os.getenv("API_BASE_URL")
token = get_token()
headers = {
    'Authorization': f'Token {token}'
}

def create_events_response(start_index: int, end_index: int, 
                           events: list[dict]) -> str:
    result = ""
    for i in range(start_index, end_index + 1):
        result += create_event_messsage(events[i])
        result += "---------------------------\n\n"
    return result


async def create_new_events_response(start_index: int, end_index: int,
                                     events: list[dict], state: FSMContext) -> str:
    result = ""
    events_to_delete = []
    for i in range(start_index, end_index + 1):
        result += create_event_messsage(events[i])
        events_to_delete.append(events[i]["id"])
        result += "---------------------------\n\n"
    data = await state.get_data()
    existing_ids = data.get("events_to_delete", [])
    unique_ids = list(set(existing_ids + events_to_delete))
    await state.update_data(events_to_delete=unique_ids)

    return result