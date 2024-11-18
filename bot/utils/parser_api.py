import logging
import os
import sys
from loader import token
from aiohttp.client_exceptions import ClientConnectionError
from utils.api_commands import get_request

logger = logging.getLogger(f"root.{__name__}")
_headers = {
    "Authorization": "Token " + token
}
API_BASE_URL = os.getenv("API_BASE_URL")
if API_BASE_URL is None:
    sys.exit("Incorrect API url")




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
async def get_events_types() -> list[dict]:
    """
    Возвращает список типов событий в виде словаря
    """
    url = API_BASE_URL + "hackaton/types/"

    return await get_request(url, headers=_headers)

@api_request_error_handler
async def get_events() -> list[dict]:
    """
    Возвращает список всех событий в виде словаря
    """
    url = API_BASE_URL + "hackaton/"

    return await get_request(url, headers=_headers)


@api_request_error_handler
async def get_events_by_preferences(events_types: list[int], tags: list[int]) -> list[dict]:
    """
        Возвращает список всех событий по предпочтению в виде словаря
    """
    url = API_BASE_URL + "hackaton/?"

    for event_type in events_types:
        url += f"type_of_event={event_type}&"

    for tag in tags:
        url += f"tags={tag}&"

    url = url[:-1]

    return await get_request(url, headers=_headers)


@api_request_error_handler
async def get_tags() -> list[dict]:
    url = API_BASE_URL + "hackaton/tags/"

    return await get_request(url, headers=_headers)

# FIXME change updates logic
@api_request_error_handler
async def get_updates() -> list[dict]:
    """
    Функция для получения новых мероприятий.
    Используется для рассылки
    """
    url = API_BASE_URL + "hackaton/update/"

    return await get_request(url)