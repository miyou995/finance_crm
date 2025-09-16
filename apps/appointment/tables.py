import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from apps.appointment.models import Appointment
from apps.core.columns import (
    ActionColumn,
    BadgeColumn,
    CustomCheckBoxColumn,
    ManyToManyBadgeColumn,
)


class AppointmentHtmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)

    counter = tables.TemplateColumn(verbose_name="N°", template_code="{{ row_counter|add:'1' }}", orderable=False,)
    lead_display = tables.Column(verbose_name=_("Lead"), accessor='lead_display', orderable=True)
    name = tables.Column(verbose_name=_("Contact/Société"), accessor='name', orderable=True)
    date = tables.Column(verbose_name=_("Date"), accessor='date', orderable=True)
    subject = tables.Column(verbose_name=_("Sujet"), accessor='subject', orderable=True)
    state = BadgeColumn("get_state_color", "get_state_display")
    users = ManyToManyBadgeColumn(accessor="users", verbose_name=_("Utilisateurs"), separator=", ", orderable=True)

    actions = ActionColumn()

    class Meta:
        model = Appointment
        template_name = "tables/bootstrap_htmx.html"
        fields = (
            "checked_row",
            "counter",
            "subject",
            "lead_display",
            "name",
            "state",
            "users",
            "date",
            "actions",
        )
        empty_text = _("Aucun rendez-vous trouvé.")
