import aiohttp
import logging
import os
import sys
from loader import token
from aiohttp.client_exceptions import ClientConnectionError
from models import *


logger = logging.getLogger(f"root.{__name__}")
_headers = {
    "Authorization": "Token " + token
}
API_BASE_URL = os.getenv("API_BASE_URL")
if API_BASE_URL is None:
    sys.exit("Incorrect API url")


async def get_request(url: str, model: type) -> list:
    """
    Функция для выолнения GET-запросов к API и парсинга полученных данных

    :param url: URL для запроса
    :param model: Модель для парсинга
    :return: list[model]
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=_headers) as response:
            data = await response.json(content_type="application/json")
            return [model.parse_obj(item) for item in data]

def api_request_error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientConnectionError:
            logger.error("Can't connect to server")
            return []
    wrapper.__name__ == func.__name__
    return wrapper


@api_request_error_handler
async def get_events_types() -> list[EventType]:
    url = API_BASE_URL + "hackaton/types/"

    return await get_request(url, EventType)

@api_request_error_handler
async def get_events() -> list[Event]:
    url = API_BASE_URL + "hackaton/"

    return await get_request(url, Event)


@api_request_error_handler
async def get_events_by_preferences(events_types: list[int], tags: list[int]) -> list[Event]:
    url = API_BASE_URL + "hackaton/?"

    for event_type in events_types:
        url += f"type_of_event={event_type}&"

    for tag in tags:
        url += f"tags={tag}&"

    url = url[:-1]

    return await get_request(url, Event)


@api_request_error_handler
async def get_tags() -> list[EventTag]:
    url = API_BASE_URL + "hackaton/tags/"

    return await get_request(url, EventTag)


@api_request_error_handler
async def get_updates() -> list[Event]:
    """
    Функция для получения новых мероприятий.
    Используется для рассылки
    """
    url = API_BASE_URL + "hackaton/update/"

    return await get_request(url,Event)