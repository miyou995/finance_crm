from django.db import models

from apps.core.models import CRUDUrlMixin, TimestampedModel

# Create your models here.


class Tags(CRUDUrlMixin, TimestampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["-created_at"]
