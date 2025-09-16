
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta

from apps.core.models import TimestampedModel

class Subscription(TimestampedModel):
    class BillingCycle(models.IntegerChoices):
        MONTHLY = 1, _("Monthly")
        QUARTERLY = 2, _("Quarterly")
        YEARLY = 3, _("Yearly")

    class States(models.TextChoices):
        ACTIVE = "active", _("Active")
        PAUSED = "paused", _("Paused")
        CANCELED = "canceled", _("Canceled")
        EXPIRED = "expired", _("Expired")

    client = models.ForeignKey("crm.company", on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    is_free_trial = models.BooleanField(default=False)
    next_payment_due = models.DateField()
    
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("paused", _("Paused")),
        ("canceled", _("Canceled")),
        ("expired", _("Expired")),
    ]
    status = models.CharField(max_length=20, choices=States.choices, default=States.ACTIVE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # recurring price
    

    def __str__(self):
        return f"{self.client} - {self.billing_cycle} ({self.status})"
    
    # --- Business Logic ---
    def days_until_due(self):
        return (self.next_payment_due - timezone.now().date()).days

    def renew(self):
        """Clone current subscription and create a new one for the next cycle."""
        start_date = self.next_payment_due
        end_date = None

        # Determine new end date & next due date
        if self.billing_cycle == "monthly":
            end_date = start_date + relativedelta(months=1)
        elif self.billing_cycle == "quarterly":
            end_date = start_date + relativedelta(months=3)
        elif self.billing_cycle == "yearly":
            end_date = start_date + relativedelta(years=1)

        # Clone subscription
        new_sub = Subscription.objects.create(
            client=self.client,
            start_date=start_date,
            end_date=end_date,
            billing_cycle=self.billing_cycle,
            next_payment_due=end_date,  # next due at end of new cycle
            status="active",
            amount=self.amount,
        )

        # Optionally mark old one as expired/canceled
        self.status = "expired"
        self.save()

        return new_sub

    def mark_expired(self):
        self.status = "expired"
        self.save()
        
    def is_paid(self):
        return self.payments.exists()
