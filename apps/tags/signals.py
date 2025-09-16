from apps.tags.models import Tags
from django.dispatch import receiver
from apps.core.utils import get_unique_slug
from django.db.models.signals import  pre_save


@receiver(pre_save, sender=Tags)
def set_tags_slug(sender, instance, **kwargs):
    if not instance.slug:
        print("\n \n _n \n \n \n SELUGGING TAGS SLUG")
        instance.slug = get_unique_slug(instance)
        print(f"Generated slug: {instance.slug} for tags: {instance.name}")
