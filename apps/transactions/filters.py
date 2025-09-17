
from django.db.models import Q
import django_filters
import django_filters.widgets
from django.contrib.auth import get_user_model
from apps.core.widgets import  SwitchWidget

from .models import (
    ClientPayment,
    LedgerEntry,
    StaffPayment,
    MiscTransaction,
)
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class FilterTransactionMixin(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label=_("Recherche"))
    created_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_("Créé par"),
        empty_label=_("Tous les utilisateurs"),
        field_name="created_by",
    )
    date = django_filters.DateFromToRangeFilter(
        label=_("Date"),
        lookup_expr="range",
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    )

    # Define the list of lookup paths in the subclass
    search_lookups = []

    def universal_search(self, queryset, name, value):

        if not value:  # Skip filtering if query is empty
            return queryset

        query = Q()
        for lookup in self.search_lookups:
            query = query | Q(**{lookup: value})
        return queryset.filter(query)

    # def universal_search(self, queryset, name, value):
    #     """
    #     Filter queryset by searching for value in all CharFields of the model
    #     and CharFields of its ForeignKey-related models (one level deep).
    #     """
    #     model = self.Meta.model
    #     query = Q()

    #     # Helper function to build Q objects for CharFields
    #     def build_charfield_queries(model, prefix='', max_depth=1, current_depth=0):
    #         q = Q()
    #         for field in model._meta.fields:
    #             if isinstance(field, CharField):
    #                 lookup = f"{prefix}{field.name}__icontains"
    #                 q = q | Q(**{lookup: value})
    #             elif isinstance(field, ForeignKey) and current_depth < max_depth:
    #                 # Get the related model
    #                 try:
    #                     related_model = field.related_model
    #                     # Build queries for CharFields in the related model
    #                     new_prefix = f"{prefix}{field.name}__"
    #                     q = q | build_charfield_queries(related_model, new_prefix, max_depth=max_depth, current_depth=current_depth + 1)
    #                 except FieldDoesNotExist:
    #                     continue
    #         return q
    #     if hasattr(model.objects, 'search'):
    #         if value:  # Only filter if value is provided
    #             queryset = model.objects.search(value)
    #     else:
    #         if value:  # Only filter if value is provided
    #             query = build_charfield_queries(model)
    #             queryset = queryset.filter(query)
    #     return queryset




class ClientPaymentFilter(FilterTransactionMixin):
    search_lookups = [
        "bill__bill_number__icontains",
        "bill__lead__company__name__icontains",
    ]

    class Meta:
        model = ClientPayment
        fields = ["query", "created_by", "date"]



class AutreTransactionFilter(FilterTransactionMixin):

    search_lookups = [
        "title__icontains",
        "description__icontains",
        "created_by__username__icontains",
        "contact__name__icontains",
    ]

    class Meta:
        model = MiscTransaction
        fields = [
            "query",
            "created_by",
            "transaction_type",
            "date",
        ]


class LedgerEntryFilter(FilterTransactionMixin):
    deleted_payment = django_filters.BooleanFilter(
        method="get_deleted_payment",
        label=_("Paiements supprimés"),
        widget=SwitchWidget,
    )

    # "amount__exact",
    search_lookups = [
        "description__icontains",
        "entry_type__icontains",
        "account__icontains",
        "created_by__icontains",
        "client_payment__bill__bill_number__icontains",
        "staff_payment__staff_member__full_name__icontains",
        "misc_transaction__description__icontains",
    ]

    class Meta:
        model = LedgerEntry
        fields = ["query", "created_by", "date"]

    def get_deleted_payment(self, queryset, name, value):
        if value:
            return queryset.filter(
                  Q(client_payment__isnull=True)
                & Q(staff_payment__isnull=True)
                & Q(misc_transaction__isnull=True)
            )
        return queryset


class StaffPaymentsFilter(FilterTransactionMixin):
    class Meta:
        model = StaffPayment
        fields = ["query", "created_by", "date", "staff_member"]
        labels = {
            "staff_member": _("Membre du personnel"),
        }

