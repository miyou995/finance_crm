from django.urls import path
from apps.notification.views import notification_drawer, mark_notification_as_read


app_name = "notification"


urlpatterns = [
    #### notification drawer
    path("notification/drawer/", notification_drawer, name="notification_drawer"),
    path(
        "notification/read/<int:notification_id>/",
        mark_notification_as_read,
        name="mark_notification_as_read",
    ),
]
