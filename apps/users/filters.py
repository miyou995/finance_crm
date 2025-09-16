from datetime import timedelta
import django_filters
from django.db.models import Q
from .models import User
from django import forms
from django.utils import timezone


class UserFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    is_superuser = django_filters.BooleanFilter(
        field_name="is_superuser",
        method="choice_filters",
        label="Superuser",
        widget=forms.CheckboxInput(),
    )
    is_staff = django_filters.BooleanFilter(
        field_name="is_staff",
        method="choice_filters",
        label="Staff",
        widget=forms.CheckboxInput,
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        method="choice_filters",
        label="Active",
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = User
        fields = ["is_active", "is_staff", "is_superuser", "groups"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    def choice_filters(self, queryset, name, value):
        if self.data.get("is_superuser") == "on":
            queryset = queryset.filter(is_superuser=True)

        if self.data.get("is_staff") == "on":
            queryset = queryset.filter(is_staff=True)

        if self.data.get("is_active") == "on":
            queryset = queryset.filter(is_active=True)
        return queryset.distinct()


class UserB2BPerformanceFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    date_range = django_filters.DateFromToRangeFilter(
        method="performance_date_filter",
        widget=django_filters.widgets.DateRangeWidget(
            attrs={"type": "date", "class": "input"}
        ),
        label="Date Range",
        initial=lambda: (
            timezone.now().date() - timedelta(days=1),
            timezone.now().date(),
        ),
    )

    class Meta:
        model = User
        fields = ["query", "date_range"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    def performance_date_filter(self, queryset, name, value):
        return queryset.include_b2b_counts(start_date=value.start, stop_date=value.stop)


class UserB2CPerformanceFilterSet(UserB2BPerformanceFilterSet):
    def performance_date_filter(self, queryset, name, value):
        return queryset.include_b2c_counts(start_date=value.start, stop_date=value.stop)


class RoleFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")

    class Meta:
        model = User.groups.through
        fields = ["query"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(name__icontains=value))
