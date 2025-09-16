from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin
from .abstract_models import (
    AbstractLeagal,
    AbstractInformation,
)
from django.db import models


class BusinessSettings(CRUDUrlMixin, AbstractLeagal, AbstractInformation):
    class Meta:
        verbose_name = _("Business Settings")
        verbose_name_plural = _("Business Settings")

    def __str__(self):
        return str(self.id)




class BusinessSocials(models.Model):
    class Socials(models.IntegerChoices):
        FACEBOOK = 1, _("Facebook")
        INSTAGRAM = 2, _("Instagram")
        TWITTER = 3, _("Twitter")
        LINKEDIN = 4, _("LinkedIn")
        PINTEREST = 5, _("Pinterest")
        SNAPCHAT = 6, _("Snapchat")
        TIKTOK = 7, _("TikTok")
        YOUTUBE = 8, _("YouTube")

    business = models.ForeignKey(
        BusinessSettings,
        on_delete=models.CASCADE,
        related_name="socials",
        verbose_name=_("Business Settings"),
    )
    social_type = models.PositiveSmallIntegerField(
        choices=Socials.choices, verbose_name=_("Social Type")
    )
    link = models.URLField(
        max_length=300, verbose_name=_("Link"), blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Is Primary"))
