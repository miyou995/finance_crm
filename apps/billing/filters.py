import django_filters
from apps.billing.models import Bill, Invoice, Quote
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from apps.crm.models.company import Company


################################# Invoice Filters ################################


class InvoiceFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    company = django_filters.ModelChoiceFilter(
        queryset=Company.objects.all(),
        method="filter_company",
        label="Company",
        field_name="company__name",
    )
    state = django_filters.ChoiceFilter(
        choices=[
            (Bill.BillStates.PENDING, _("En attente")),
            (Bill.BillStates.PAID, _("Payé")),
        ],
        label="State",
        field_name="state",
    )

    class Meta:
        model = Invoice
        fields = ["state", "company"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(bill_number__icontains=value) | Q(notes__icontains=value)
        )

    def filter_company(self, queryset, name, value):
        if value:
            return queryset.filter(lead__company=value)
        return queryset


############################# Quote Filters #############################


class QuoteFilterSet(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="Search")
    company = django_filters.ModelChoiceFilter(
        queryset=Company.objects.all(),
        method="filter_company",
        label="Company",
        field_name="company__name",
    )
    state = django_filters.ChoiceFilter(
        choices=[
            (Bill.BillStates.PENDING, _("En attente")),
            (Bill.BillStates.ACCEPTED, _("Accepté")),
            (Bill.BillStates.SENT, _("Envoyé")),
        ],
        label="State",
        field_name="state",
    )

    class Meta:
        model = Quote
        fields = ["state", "company"]

    def universal_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(bill_number__icontains=value) | Q(notes__icontains=value)
        )

    def filter_company(self, queryset, name, value):
        if value:
            return queryset.filter(lead__company=value)
        return queryset
