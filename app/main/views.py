
from django.db.models import Count
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, Tag, EventTypeClassifier, HistoryUserRequest, BotUser
from .serializer import EventSerializer, TagSerializer, EventTypeSerializer, BotUserSerializer
from django.db.models.query import QuerySet


def filter_by_type(types: list,
                   events_for_filtering: QuerySet) -> QuerySet | list:
    """
    метод для фильтрации мероприятий по типу (конференция, хакатон, итд)
    :param types: список с типами которые надо получить
    :param events_for_filtering:  список мероприятий для фильтрации
    :return: отфилтрованный по типам QuerySet или пустой список так как совпадений не было
    """
    rez = []
    for type_of_event in types:
        half_rez = events_for_filtering.filter(
            type_of_event=int(type_of_event))
        if len(rez) == 0:
            rez = half_rez
        else:
            rez = rez.union(half_rez)
    return rez


def filter_by_tag(tags: list,
                  events_for_filtering: QuerySet) -> QuerySet | list:
    """
     метод для фильтрации мероприятий по тегу (Искусственный интеллект, Управление данными, итд)
     :param tags: список с тегами которые надо получить
     :param events_for_filtering:  список мероприятий для фильтрации
     :return: отфилтрованный по типам QuerySet или пустой список так как совпадений не было
     """
    rez = []
    for i in tags:
        half_rez = Event.objects.filter(
            id__in=events_for_filtering.values('id'))
        half_rez = half_rez.filter(tags__tag_code=int(i))
        if len(rez) == 0:
            rez = half_rez
        else:
            rez = rez.union(half_rez)
    return rez


class TypeTitleAPIView(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = EventSerializer

    def get_queryset(self):
        """
        апи для мерорпиятий
        параметры фильтрации:
            тег: один или много => tags
            тип события: один или много => type_of_event
        критерии для фильтрации передаются в запросе как параметры
        """
        all_events = Event.objects.all()
        type_of_event_get = self.request.query_params.getlist('type_of_event')
        tags = self.request.query_params.getlist('tags')

        if len(type_of_event_get) != 0:
            rez = filter_by_type(types=type_of_event_get,
                                 events_for_filtering=all_events)
            if len(tags) != 0:
                rez = filter_by_tag(tags=tags, events_for_filtering=rez)
        else:
            rez = filter_by_tag(tags=tags, events_for_filtering=all_events)

        if len(type_of_event_get) == 0 and len(tags) == 0:
            rez = all_events
        return rez.order_by('start_date')


class HackatonUpdateAPIView(generics.UpdateAPIView):
    pass


class TagAPIView(generics.ListAPIView):
    """
    апи для всех тегов, фильтроции нет
    """
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class EventTypeAPIView(generics.ListAPIView):
    """
    апи для всех типов, фильтроции нет
    """
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = EventTypeClassifier.objects.all()
    serializer_class = EventTypeSerializer


class UserProfileListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BotUserSerializer
    queryset = BotUser.objects.all()


class UserProfileAPIViewSet(viewsets.ModelViewSet):
    queryset = BotUser.objects.all()
    serializer_class = BotUserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'], url_path='remove-new-events')
    def remove_new_events(self, request, pk=None):
        user = self.get_object()
        print("Received data:", request.data)
        if not request.data:
            return Response(
                {"detail": "Нет данных для обработки."},
                status=status.HTTP_400_BAD_REQUEST
            )
        event_ids_to_remove = request.data.get('remove', [])
        if not isinstance(event_ids_to_remove, list):
            print("not list")
            return Response(
                {"detail": "'remove' должен быть списком идентификаторов событий."},
                status=status.HTTP_400_BAD_REQUEST
            )
        events_to_remove = Event.objects.filter(id__in=event_ids_to_remove)
        if events_to_remove.count() != len(event_ids_to_remove):
            print("not all events exist")
            return Response(
                {"detail": "Некоторые события не существуют."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.new_events.remove(*events_to_remove)
        serializer = EventSerializer(user.new_events.all(), many=True)
        return Response(
            {
                "detail": "События успешно удалены из new_events.",
                "new_events": serializer.data
            },
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=['get'], url_path='new-events')
    def new_events(self, request, pk=None):
        user = self.get_object()
        new_events = user.new_events.all()
        serializer = EventSerializer(new_events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='toggle-mailing-status')
    def toggle_mailing_status(self, request, pk=None):
        user = self.get_object()
        user.mailing_status = not user.mailing_status
        if (not(user.mailing_status)):
            try:
                history = HistoryUserRequest.objects.get(user=user.id)
                history.delete()
            except HistoryUserRequest.DoesNotExist:
                pass
        user.save()
        return Response({'mailing_status': user.mailing_status})

    @action(detail=True, methods=['patch'], url_path='toggle-mailing-all')
    def update_mailing_type(self, request, pk=None):
        user = self.get_object()
        user.mailing_all = not user.mailing_all
        user.save()
        return Response({'mailing_all': user.mailing_all})

    @action(detail=True, methods=['patch'], url_path='toggle-notification-status')
    def toggle_notification_status(self, request, pk=None):
        user = self.get_object()
        user.notification_status = not user.notification_status
        user.save()
        return Response({'notification_status': user.notification_status})

    @action(detail=True, methods=['patch'], url_path='change-event-preference')
    def change_event_preference(self, request, pk=None):
        user = self.get_object()
        event_types = request.data.get('event_preferences')
        if not isinstance(event_types, list):
            return Response(
                {'Error': 'event_preferences должен быть списком вида type_code.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            event_type_objs = EventTypeClassifier.objects.filter(type_code__in=event_types)
            user.event_preferences.set(event_type_objs)
            user.save()
            return Response(
                {'event_preferences': user.event_preferences.values_list('type_code', flat=True)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'Error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='change-tag-preferences')
    def change_tag_preference(self, request, pk=None):
        user = self.get_object()
        tag_types = request.data.get('tag_preferences')
        if not isinstance(tag_types, list):
            return Response(
                {'Error': 'tag_preferences должен быть списком вида [tag_code1, tag_code2, ..].'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            tag_type_objs = Tag.objects.filter(tag_code__in=tag_types)
            user.tag_preferences.set(tag_type_objs)
            user.save()
            return Response(
                {'tag_preferences': user.tag_preferences.values_list('tag_code', flat=True)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'Error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

