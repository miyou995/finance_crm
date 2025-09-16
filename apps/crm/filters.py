import django_filters
from apps.core.widgets import BooleanAllSelect
from apps.crm.models.company import ActivitySector, Company
from apps.crm.models.contact import Contact
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.tags.models import Tags


class ContactFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")


    class Meta:
        model = Contact
        fields = ["company", "civility", "source"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(full_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(company__name__icontains=value)
            | Q(civility__icontains=value)
        )



class CompanyFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    activity_sectors = django_filters.ModelChoiceFilter(
        queryset=ActivitySector.objects.all(),
        method="filter_activity_sector",
        label="Secteur d'activité",
        field_name="activity_sectors",
    )

    tags = django_filters.ModelChoiceFilter(
        queryset=Tags.objects.all(),
        method="filter_tags",
        label="Tags",
        field_name="tags",
    )



    class Meta:
        model = Company
        fields = ["activity_sectors", "wilaya", "tags"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(name__icontains=value) | Q(business_owner__icontains=value)
        )
    def filter_activity_sector(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(activity_sectors=value)

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(tags=value)
