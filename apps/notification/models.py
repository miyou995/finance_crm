from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import CRUDUrlMixin, TimestampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(CRUDUrlMixin, TimestampedModel):
    class States(models.IntegerChoices):
        NOTIFICATION = 1, _("Notification")
        # APPOINTMENT = 2, _("Rendez-vous")
        RECALL = 3, _("Rappel")
        TASK = 4, _("Tâche")

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications_sent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # generic relationship to any model
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    date = models.DateTimeField()
    message = models.TextField()
    state = models.PositiveSmallIntegerField(
        choices=States.choices, default=States.NOTIFICATION
    )
    link = models.URLField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return self.message[:50]  # Return first 50 characters of the message

    @property
    def get_state_color(self):
        state = self.state
        if state == 1:
            return "success"
        elif state == 3:
            return "warning"
        elif state == 4:
            return "danger"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()
        print(f"Notification {self.id} marked as read.")
