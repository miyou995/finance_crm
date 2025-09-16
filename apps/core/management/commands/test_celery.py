from django.core.management.base import BaseCommand
from apps.notification.tasks import (
    send_notification_b2b_no_invoice_6months,
)


class Command(BaseCommand):
    help = "Runs Celery worker with the specified settings"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Celery worker..."))

        result = send_notification_b2b_no_invoice_6months()
        print(
            "Celery worker started with the task send_notification_b2b_no_invoice_6months"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Task send_notification_b2b_no_invoice_6months result: {result}"
            )
        )
