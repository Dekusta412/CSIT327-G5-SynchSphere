from django.contrib import admin
from .models import Event, Reminder, Notification, UserProfile

admin.site.register(Event)
admin.site.register(Reminder)
admin.site.register(Notification)
admin.site.register(UserProfile)


