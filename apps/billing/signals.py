from django.db.models.signals import pre_save, post_save
from apps.billing.models import Invoice, Quote
from django.dispatch import receiver


@receiver(pre_save, sender=Invoice)
def invoice_number_created(sender, instance, **kwargs):
    if not instance.bill_number:
        year = instance.creation_date.year
        instance.bill_number = instance.generate_bill_number(year)
        instance.save()
        print(f"from signal----------------->>>>>>>>Invoice number set: {instance.bill_number} for year {year}")


@receiver(post_save, sender=Quote)
def quote_number_created(sender, instance, **kwargs):
    if not instance.bill_number:
        year = instance.creation_date.year
        instance.bill_number = instance.generate_bill_number(year)
        instance.save()
