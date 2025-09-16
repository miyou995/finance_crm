from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.billing.models import Invoice
from apps.crm.models.company import Company
from apps.notification.models import Notification
from django.db.models import Max

def payment_mixin(num_days):
    now = timezone.now()
    today = now.date()
    invoice = Invoice.objects.filter(
        due_date__gte=today,
        due_date__lte=today + timezone.timedelta(days=num_days),
        state=Invoice.States.PENDING,
    ).select_related("lead")
    for inv in invoice:
        Notification.objects.create(
            recipient=inv.created_by,
            state=Notification.States.NOTIFICATION,
            content_object=inv,
            date=today,
            link=inv.get_absolute_url(),
            message=f"Le paiement de la facture {inv.bill_number} est dû dans {num_days} jours.",
        )
    return f"Notification sent for {len(invoice)} invoices due in {num_days} jours."


@shared_task
def send_notification_deadline_payment_5days():
    print("Sending notification for 5 days payment deadline ===> YES\n s")
    return payment_mixin(5)


@shared_task
def send_notification_deadline_payment_30days():
    return payment_mixin(30)


@shared_task
def send_notification_deadline_payment_2days():
    return payment_mixin(2)


@shared_task
def send_notification_deadline_payment_1day():
    return payment_mixin(1)


@shared_task
def send_notification_b2b_no_invoice_6months():
    now = timezone.now()
    today = now.date()
    six_months_ago = today - timezone.timedelta(days=180)
    # invoices = Invoice.objects.filter(created_at__lte=six_months_ago).distinct()
    last_invoice_in_each_company = (
        Invoice.objects.filter(created_at__lte=six_months_ago)
        .values("lead__company")
        .annotate(last_invoice_date=Max("created_at"))
    )
    for invoice in last_invoice_in_each_company:
        company_id = invoice["lead__company"]
        last_invoice_date = invoice["last_invoice_date"]
        # Get the actual Invoice instance
        invoice = Invoice.objects.filter(
            lead__company_id=company_id,
            created_at=last_invoice_date
        ).select_related("lead__company", "created_by").first()
        
        Notification.objects.create(
            recipient=invoice.created_by,
            state=Notification.States.NOTIFICATION,
            content_object=invoice,
            link=get_object_or_404(
                Company, id=invoice.lead.company.id
            ).get_absolute_url(),
            # link=invoice.get_absolute_url(),
            date=today,
            message=f"Aucun opportunité n'a été effectué pour la société {invoice.lead.company} depuis 6 mois.",
        )

    return f"Notifications sent for {last_invoice_in_each_company.count()} B2B leads with no invoices in the last 6 months."
 