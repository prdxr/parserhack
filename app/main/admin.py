from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from .models import *


admin.site.register(EventTypeClassifier)
admin.site.register(Event)
admin.site.register(Tag)
admin.site.register(Keyword)
admin.site.register(HistoryUserRequest)
admin.site.register(BotUser)
