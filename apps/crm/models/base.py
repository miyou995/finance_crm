from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class AbstractEmail(TimestampedModel):
    email = models.EmailField(_("Email"))

    def __str__(self):
        return self.email

    class Meta:
        abstract = True


class AbstractPhone(TimestampedModel):
    phone = models.CharField(_("Phone"), max_length=20)

    def __str__(self):
        return self.phone

    class Meta:
        abstract = True
