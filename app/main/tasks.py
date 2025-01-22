import json
import logging
import os
import time
from datetime import datetime

import requests
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .parsers.utils import clean_event
from .models import Event, BotUser, HistoryUserRequest
from .parsers import *
from .tagger import all_events_tagger


logger = logging.getLogger("app.tasks")
TG_API_URL = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"


@shared_task
def notify_users() -> None:
    """
    Метод для отправки уведомлений пользователям.
    Назначается на определённый период в админке
    """
    logger.info("Запуск задачи notify_users")
    try:
        users = BotUser.objects.filter(notification_status=True).prefetch_related('new_events')
        logger.info(f"Найдено пользователей для уведомления: {users.count()}")
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей: {e}", exc_info=True)
        return

    for user in users:
        user_id = user.id
        user_tg = user.telegram_id
        if not user.new_events.exists():
            logger.info(f"У пользователя {user_id} нет новых событий")
            continue

        user_events = user.new_events.all()
        user_events_count = user_events.count()
        if user_events_count == 0:
            logger.info(f"У пользователя {user_id} нет новых событий")
            continue
        data = {
            'chat_id': user_tg,
            'text': f"У вас есть непрочитанные события ({user_events_count})",
            'reply_markup': json.dumps({
            "inline_keyboard": [
                [
                    {
                        "text": "Показать мероприятия",
                        "callback_data": "/notification_events"
                    }
                ]
            ]
        })}
        logger.info(f"Найдено {user_events_count} новых событий для пользователя {user_id}")

        try:
            requests.post(TG_API_URL, data=data)
            logger.info(f"Уведомления отправлены пользователю {user_id}")
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомлений пользователю {user_id}: {e}", exc_info=True)

    logger.info('Задача notify_users завершена')

@shared_task
def clean_database() -> None:
    """
    Метод для периодической очистки базы данных.
    Назначается на определённый период в админке
    """
    logger.info("Запуск задачи clean_database")
    saved_hackathons = Event.objects.all()
    count_if_deleted_events = 0
    for event in saved_hackathons:
        if event.is_expired():
            try:
                event.delete()
                count_if_deleted_events += 1
                logger.debug(f"Удалено событие: {event.id}")
            except Exception as e:
                logger.error(f"Ошибка при удалении события {event.id}: {e}", exc_info=True)

    logger.info(f'Завершено, удалено {count_if_deleted_events} событий')


@shared_task
def parse_new_events() -> None:
    """
    Метод для сбора новой информации с сайтов.
    Реализовано посредством запуска всех парсеров,
    и дальнейшего сохранения полученных мероприятий.
    Назначается на определённый период в админке
    """
    logger.info("Запуск задачи parse_new_events")
    all_threads = [
        get_codenrock_events,
        get_all_events,
        get_hackathon_com_events,
        get_ict2go_events, get_leader_id_events,
        get_na_conferencii_events, get_2035_university_events
    ]

    time_start = datetime.now()
    return_rez: list[Event] = []
    for task in all_threads:
        try:
            rez = task()
            logger.info(f"{task.__name__} - получено {len(rez)} событий")
            return_rez += rez
        except KeyError as e:
            logger.error(f"KeyError в парсере {task.__name__}: {e}", exc_info=True)
        except RuntimeError as e:
            logger.error(f"RuntimeError в парсере {task.__name__}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Неизвестная ошибка в парсере {task.__name__}: {e}", exc_info=True)

    for event in return_rez:
        try:
            clean_event(event)
            logger.debug(f"Обработано событие: {event.id}")
        except Exception as e:
            logger.error(f"Ошибка при очистке события {event.id}: {e}", exc_info=True)

    time_end = datetime.now() - time_start
    logger.info(f"Время выполнения парсинга: {time_end}")
    logger.info(f"Всего получено событий: {len(return_rez)}")

    for event in return_rez:
        try:
            if not event.already_exists():
                event.save()
                logger.debug(f"Сохранено новое событие: {event.id}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении события {event.id}: {e}", exc_info=True)

    try:
        all_events_tagger()
        logger.info("Тэггирование событий завершено")
    except Exception as e:
        logger.error(f"Ошибка при тэггировании событий: {e}", exc_info=True)

    try:
        update_users_new_events()
        logger.info("Обновление пользователей новыми событиями завершено")
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователей: {e}", exc_info=True)

    logger.info('Задача parse_new_events завершена')


def update_users_new_events():
    """
    Задача для пополнения новых мероприятий у пользователей
    """
    logger.info("Запуск функции update_users_new_events")
    try:
        users = BotUser.objects.filter(mailing_status=True).prefetch_related(
            'event_preferences', 'tag_preferences', 'new_events'
        )
        logger.info(f"Найдено пользователей для обновления: {users.count()}")
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей: {e}", exc_info=True)
        return

    for user in users:
        user_id = user.id
        try:
            current_user_history = HistoryUserRequest.objects.get(user_id=user_id)
            logger.info(f"Найдена запись истории запроса для пользователя {user_id}")
        except ObjectDoesNotExist:
            current_user_history = HistoryUserRequest.objects.create(user_id=user_id)
            logger.info(f"Создана запись истории запроса для пользователя {user_id}")

        result_queryset = Event.objects.filter(
            date_of_parsing__gte=current_user_history.time_of_last_request
        )

        filter_conditions = Q()

        if user.event_preferences.exists():
            filter_conditions |= Q(type_of_event__in=user.event_preferences.all())
            logger.info(f"Применены фильтры по типам событий для пользователя {user_id}")

        if user.tag_preferences.exists():
            filter_conditions |= Q(tags__in=user.tag_preferences.all())
            logger.info(f"Применены фильтры по тегам для пользователя {user_id}")


        if user.mailing_all is True:
            result_queryset = result_queryset.distinct()
            logger.info(f"Показаны все новые ({result_queryset.count()}) события для пользователя {user_id}")

        else:
            result_queryset = result_queryset.filter(filter_conditions).distinct()
            logger.info(f"Отфильтровано {result_queryset.count()} событий для пользователя {user_id}")


        if result_queryset.exists():
            try:
                user.new_events.add(*result_queryset)
                logger.info(f"Добавлено {result_queryset.count()} новых событий для пользователя {user_id}")
            except Exception as e:
                logger.error(f"Ошибка при добавлении событий пользователю {user_id}: {e}", exc_info=True)
                continue

        try:
            current_user_history.time_of_last_request = datetime.now()
            current_user_history.save()
            logger.info(f"Обновлено время последнего запроса для пользователя {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении истории запроса для пользователя {user_id}: {e}", exc_info=True)

