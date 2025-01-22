import re
import logging

import html
import requests
from bs4 import BeautifulSoup

from main.models import *
from .utils import get_event_types, HTML_TAG_CLEANER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_events():
    BASIC_URL = "https://all-events.ru/events/calendar/theme-is-upravlenie_personalom_hr-or-informatsionnye_tekhnologii-or-automotive_industry-or-bezopasnost-or-blokcheyn_kriptovalyuty-or-innovatsii-or-it_telecommunications-or-elektronnaya_kommertsiya/type-is-conferencia-or-hackathon-or-contest"

    event_types = get_event_types()
    events = []

    try:
        response = requests.get(BASIC_URL, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.RequestException as e:
        logger.error(f"Failed to fetch the page: {e}")
        return events

    try:
        html_decoded_string = html.unescape(response.text)
        raw_page = BeautifulSoup(html_decoded_string, "html.parser")
    except Exception as e:
        logger.error(f"Failed to parse the HTML: {e}")
        return events

    raw_events_list = raw_page.select('div.event-wrapper')
    raw_events_additional_info_list = raw_page.select('div.event_flex_item')

    if len(raw_events_list) != len(raw_events_additional_info_list):
        logger.warning("Mismatch in the number of events and additional info")

    raw_events = list(zip(raw_events_list, raw_events_additional_info_list))

    for raw_event, event_additional_data in raw_events:
        try:
            event = parse_event(raw_event, event_additional_data, event_types)
            if event:
                events.append(event)
        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            continue

    return events


def parse_event(raw_event, event_additional_data, event_types):
    event = Event()

    try:
        event.title = raw_event.select_one('div.event-title').text.strip()
    except AttributeError:
        logger.warning(f"Could not find title for event")
        return None

    try:
        description_items = raw_event.select_one('span[itemprop="description"]').stripped_strings
        description = " ".join(description_items)
        description = re.sub(HTML_TAG_CLEANER, "", description)
        event.description = description.replace("\t", "").replace("\r", "").replace("\n\n\n", "\n").replace("\n\n",
                                                                                                            "\n")
    except AttributeError:
        logger.warning(f"Could not find description for event: {event.title}")

    try:
        tags = raw_event.select('div.teg_content a')
        for tag in tags:
            event.description += f". {tag.text}"
    except Exception:
        logger.warning(f"Could not process tags for event: {event.title}")

    try:
        raw_start_date = raw_event.select_one('div[itemprop="startDate"]')['content']
        event.start_date = datetime.fromisoformat(raw_start_date)
        raw_end_date = raw_event.select_one('div[itemprop="endDate"]')['content']
        event.end_date = datetime.fromisoformat(raw_end_date)

        moscow_tz = timezone(timedelta(hours=3))
        event.start_date = event.start_date.astimezone(moscow_tz)
        event.end_date = event.end_date.astimezone(moscow_tz)

        if event.start_date < datetime.now(tzlocal()).astimezone(moscow_tz):
            return None
    except Exception as e:
        logger.error(f"Failed to process dates for event {event.title}: {e}")
        return None

    try:
        event.url = "https://all-events.ru" + raw_event.select_one('a[itemprop="url"]')['href']
    except AttributeError:
        logger.warning(f"Could not find URL for event: {event.title}")

    try:
        address_element = raw_event.select_one('div.event-venue div.address span[itemprop="addressLocality"]')
        event.address = address_element.text if address_element else ""
    except Exception:
        logger.warning(f"Could not find address for event: {event.title}")

    try:
        raw_event_type_element = event_additional_data.select_one(
            'div.event_info_new a.event_info_new_text.mob_name_event span:not([class])')
        raw_event_type = raw_event_type_element.text if raw_event_type_element else ""

        if raw_event_type not in event_types.keys():
            logger.warning(f"Unknown event type for event: {event.title}")
            return None

        event.type_of_event = EventTypeClassifier.objects.get(type_code=event_types[raw_event_type])
    except Exception as e:
        logger.error(f"Failed to process event type for {event.title}: {e}")
        return None

    try:
        raw_event_cost_type_element = raw_event.select_one('div.event-price')
        raw_event_cost_type = raw_event_cost_type_element['content'].strip() if raw_event_cost_type_element else ""

        if raw_event_cost_type == "Бесплатно":
            event.is_free = True
        elif raw_event_cost_type and raw_event_cost_type[-1].isdigit():
            event.is_free = False
        else:
            logger.warning(f"Unclear event cost type for event: {event.title}")
    except Exception:
        logger.warning(f"Could not determine if event is free: {event.title}")

    return event
