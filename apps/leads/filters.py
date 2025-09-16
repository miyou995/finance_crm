import django_filters
from django.db.models import Q
from .models import B2BLead, B2CLead
from django.forms.widgets import DateInput
from django.contrib.auth import get_user_model

User = get_user_model()


class B2bLeadFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    start_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Prospect ajouté après le ('Début')",
        widget=DateInput(attrs={"type": "date"}),
    )
    end_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Prospect ajouté avant le ('Fin')",
        widget=DateInput(attrs={"type": "date"}),
    )
    # state = django_filters.ChoiceFilter(field_name='current_state', choices=LEAD_STATE_CHOICES, label="état")
    # agent = django_filters.ModelChoiceFilter(field_name='current_state_user', queryset=User.objects.filter(is_commercial=True), label="Agent")
    # interest = django_filters.ModelChoiceFilter(field_name='interest', queryset=CategoryInterest.objects.all(), label="Interest")
    # wilaya = django_filters.ModelChoiceFilter(field_name='wilaya', queryset=Wilaya.objects.all(), label="Wilaya")
    # bank = django_filters.ModelChoiceFilter(field_name='bank', queryset=Bank.objects.all(), label="Bank")
    # origin = django_filters.ModelChoiceFilter(field_name='origin', queryset=Origin.objects.all(), label="Origin")
    # is_blacklisted = django_filters.BooleanFilter(field_name='is_blacklisted', label="Blacklisted")

    class Meta:
        model = B2BLead
        fields = ["query", "company", "current_state_user", "start_date", "end_date"]

    def __init__(self, *args, **kwargs):
        super(B2bLeadFilter, self).__init__(*args, **kwargs)

    def universal_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(company__name__icontains=value)
        )


class B2cLeadFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    start_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Prospect ajouté après le ('Début')",
        widget=DateInput(attrs={"type": "date"}),
    )
    end_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Prospect ajouté avant le ('Fin')",
        widget=DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = B2CLead
        fields = ["query", "contact", "start_date", "end_date"]

    def __init__(self, *args, **kwargs):
        super(B2cLeadFilter, self).__init__(*args, **kwargs)

    def universal_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value))
