from datetime import datetime
from celery import shared_task
from .parsers.utils import clean_event
from .models import Event
from .parsers import *
from .tagger import all_events_tagger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('/var/log/cellery.app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

@shared_task
def clean_database() -> None:
    """
    Метод для переодической очстки базы данных.
    Назначается на опеределенный периуд в админке
    """
    logger.info(f'clean_database started')
    saved_hackatons = Event.objects.all()
    count_if_deleted_events = 0
    for event in saved_hackatons:
        if event.is_expired():
            logger.info(f'{event.title} is expired at {event.end_date}')
            event.delete()
            count_if_deleted_events += 1
    logger.info(f'clean_database ended, {count_if_deleted_events} deleted')

@shared_task
def parse_new_events() -> None:
    logger.info(f'parse started')
    """
    метод для сбора новый информации с сайтав.
    Реализовано по средствам запуска всех парсеров,
    и дальнейшеее сохранение полученных мероприятий.
    Назначается на опеределенный периуд в админке
    """
    all_threads = [
        get_all_events, get_hackathon_com_events,
        get_ict2go_events, get_leader_id_events, get_leaders_of_digital_events,
        get_na_conferencii_events, get_2035_university_events
    ]

    time_start = datetime.now()
    return_rez: list[Event] = []
    for task in all_threads:
        try:
            rez = task()
            logger.info(task.__str__() + " - " + str(len(rez)))

            return_rez += rez
        except KeyError:
            logger.warning("key error")
        except RuntimeError:
            logger.warning("runtime error")
        except Exception as e:
            logger.warning("error " + str(e))
            logger.warning(e.args)

    for event in return_rez:
        clean_event(event)

    time_end = datetime.now() - time_start
    events_count = 0
    error_count = 0
    for event in return_rez:
        try:
            if not event.already_exists():
                event.save()
                logger.info(f'{event.title} saved')
                events_count += 1
        except Exception as e:
            error_count += 1
            logger.warning("error in saving " + str(e))
    all_events_tagger()
    logger.info(f'parse ended in {time_end}. {len(return_rez)} parsed. {events_count} saved. {error_count} errors occured.')