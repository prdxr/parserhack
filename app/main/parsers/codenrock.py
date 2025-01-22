import logging

import requests

from main.models import *
from .utils import get_event_types

def get_contests():
    url = 'https://codenrock.com/contests'
    params = {
        'take': '10',
        'is_home': '0',
        'page': '1',
        'status': '',
        'search': '',
        'tags': '',
        'communities_ids': ''
    }
    headers = {
        'authority': 'codenrock.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://codenrock.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_codenrock_events():
    response = get_contests()
    if response is None:
        logging.error("Error parsing response from codenrock")

    event_types = get_event_types()
    events = []

    for hack in response['contests']:
        if hack["type"] == "test":
            continue

        event = Event()

        event.title = hack["name"]
        event.description = hack["meta_description"]

        event.start_date = datetime.fromisoformat(hack["start_date"])
        event.end_date = datetime.fromisoformat(hack["end_date"])
        moscow_tz = timezone(timedelta(hours=3))
        event.start_date = event.start_date.astimezone(moscow_tz)
        event.end_date = event.end_date.astimezone(moscow_tz)

        event.url = "https://codenrock.com/contests/" + hack["slug"]
        event.address = "Проверять по ссылке\n" + "Тип: " + hack["location"]

        event.type_of_event = EventTypeClassifier.objects.get(type_code=event_types["Хакатон"])

        tags = [tag['name_ru'] for tag in hack["tags"]]

        event.description += "Теги:\n"
        for tag in tags:
            event.description += f"{tag}\n"

        event.is_free = True

        events.append(event)

    return events
