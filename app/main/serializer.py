from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import Event, Tag, EventTypeClassifier, BotUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTypeClassifier
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    type_of_event = EventTypeSerializer(read_only=True)

    class Meta:
        model = Event
        exclude = ['date_of_parsing']

class BotUserCreateSerializer(UserCreateSerializer):
    telegram_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta(UserCreateSerializer.Meta):
        model = BotUser
        fields = ('username', 'password', 'telegram_id')

class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = ['id', 'username', 'telegram_id','event_preferences','tag_preferences',
        'new_events', 'mailing_all', 'mailing_status', 'notification_status']

