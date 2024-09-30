from bot.models.Event import Event
from bot.utils.create_event_message import create_event_messsage


def create_events_response(start_index: int, end_index: int, 
                           events: list[Event]) -> str:
    result = ""
    for i in range(start_index, end_index + 1):
        result += create_event_messsage(events[i])
        result += "---------------------------\n\n"
    
    return result
