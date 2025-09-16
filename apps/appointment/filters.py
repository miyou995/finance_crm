from django.forms import DateInput
from apps.appointment.models import Appointment
import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class AppointmentFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label=_("Search"))
    b2b_or_b2c = django_filters.ChoiceFilter(
        choices=[
            ("b2b", _("B2B")),
            ("b2c", _("B2C")),
        ],
        label=_("type d'opportunité"),
        method="filter_b2b_or_b2c",
    )
    start_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        label="Rendez-vous après le ('Début')",
        widget=DateInput(attrs={"type": "date"}),
    )
    end_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        label="Rendez-vous avant le ('Fin')",
        widget=DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Appointment
        fields = ["b2b_or_b2c", "state"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        value = str(value).strip()
        q = Q(subject__icontains=value)

        if value.isdigit():
            num = int(value)
            q |= Q(id=num) | Q(b2b_lead_id=num) | Q(b2c_lead_id=num) | Q(state=num)

        q |= Q(b2b_lead__company__name__icontains=value)
        q |= Q(b2c_lead__contact__full_name__icontains=value)

        return queryset.filter(q).distinct()

    def filter_b2b_or_b2c(self, queryset, name, value):
        if value == "b2b":
            return queryset.filter(b2b_lead__isnull=False)
        elif value == "b2c":
            return queryset.filter(b2c_lead__isnull=False)
        return queryset
