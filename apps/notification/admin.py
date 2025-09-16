from django.contrib import admin

from apps.notification.models import Notification

# Register your models here.


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "sender", "message", "date", "state", "is_read")
    list_filter = ("recipient", "state", "is_read")
    search_fields = ("message",)
    ordering = ("-date",)
