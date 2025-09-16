from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tinymce import models as tinymce_models
from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.leads.models import B2BLead, B2CLead
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class AppointmentQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("appointment.view_appointment"):
            # print('user.is_staff and has_perm')
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            # print('User.objects.filter(supervisor=user).exists()')
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(Q(users__in=[user.id]) | Q(users__in=user_team_ids))
        elif user.is_commercial:
            # print('user.is_commercial')
            return self.filter(Q(users__in=[user.id]))
        else:
            return self.none()


class Appointment(CRUDUrlMixin, TimestampedModel):
    class States(models.IntegerChoices):
        Valid = 1, _("Validé")
        Pending = 2, _("En attente")
        Cancelled = 3, _("Annulé")
        Rescheduled = 4, _("Reporté")
        Completed = 5, _("Terminé")
        NoShow = 6, _("Absent")

    b2b_lead = models.ForeignKey(
        B2BLead,
        on_delete=models.CASCADE,
        related_name="appointments",
        blank=True,
        null=True,
    )
    b2c_lead = models.ForeignKey(
        B2CLead,
        on_delete=models.CASCADE,
        related_name="appointments",
        blank=True,
        null=True,
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="appointments", blank=True
    )
    state = models.PositiveSmallIntegerField(
        choices=States.choices, default=States.Pending
    )
    date = models.DateTimeField()
    subject = models.CharField(max_length=200)

    notes = tinymce_models.HTMLField(verbose_name=_("Notes"),  null=True,blank=True)
    report = tinymce_models.HTMLField(verbose_name=_("compte rendu de rendez-vous"),  null=True,blank=True)


    objects = AppointmentQueryset.as_manager()

    def __str__(self):
        return f"rendez-vous le {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ["date"]
        verbose_name = _("rendez-vous")
        verbose_name_plural = _("rendez-vous")

    @classmethod
    def get_create_url(cls, lead_b2b_pk=None, lead_b2c_pk=None):
        if lead_b2b_pk:
            return reverse(
                "appointment:create_lead_b2b_appointment",
                kwargs={"lead_b2b_pk": lead_b2b_pk},
            )
        elif lead_b2c_pk:
            return reverse(
                "appointment:create_lead_b2c_appointment",
                kwargs={"lead_b2c_pk": lead_b2c_pk},
            )
        else:
            return reverse("appointment:create_appointment")

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("appointment:bulk_delete_appointment")

    @property
    def get_state_color(self):
        state = self.state
        if state == 1:
            return "success"
        elif state == 2:
            return "warning"
        elif state == 3:
            return "danger"
        elif state == 4:
            return "primary"
        elif state == 5:
            return "info"
        elif state == 6:
            return "dark"
