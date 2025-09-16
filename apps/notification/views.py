import json
from django.http import HttpResponse
from django.shortcuts import render
from apps.notification.models import Notification


def notification_drawer(request):
    context = {}
    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by("-created_at")
    context["notifications"] = notifications
    # You can customize it to fetch notifications from your database or any other source
    return render(request, "snippets/notification_drawer.html", context)


def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(pk=notification_id, recipient=request.user)
    notification.mark_as_read()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "refresh_list": None,
                }
            )
        },
    )
