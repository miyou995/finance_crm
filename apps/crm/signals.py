from django.dispatch import receiver

from apps.core.utils import get_unique_slug
from .models.company import Company
from django.db.models.signals import pre_save


@receiver(pre_save, sender=Company)
def set_company_slug(sender, instance, **kwargs):
    if not instance.slug:
        print("\n \n _n \n \n \n SELUGGING COMPANY SLUG")
        instance.slug = get_unique_slug(instance)
        print(f"Generated slug: {instance.slug} for company: {instance.name}")
