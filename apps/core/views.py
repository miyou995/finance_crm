import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from apps.billing.models import Invoice
from apps.core.mixins import BaseManageHtmxFormView, DeleteMixinHTMX
from apps.core.models import LeadSource, Potential, Tax
from apps.transactions.models import (
    ClientPayment,
    MiscTransaction,
    StaffPayment,
)

from .forms import LeadSourceModelForm, PotentialModelForm, TaxModelForm
from .tables import LeadSourceHTMxTable, PotentialHTMxTable, TaxHTMxTable

logger = logging.getLogger(__name__)


def set_language(request, language="fr"):
    lang_code = language
    translation.activate(lang_code)
    request.session[settings.LANGUAGE_SESSION_KEY] = lang_code
    request.user.language = lang_code
    request.user.save()

    response = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


class IndexView(TemplateView):
    template_name = "tables/table_partial.html"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-850px"
        # context["ledger_table"]= LedgerEntryTable(data=LedgerEntry.objects.filter(date=date.today()))
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["index.html"]


# ----------------------------------Configuration----------------------------------


class ConfigugrationView(
    TemplateView
):  # this is a generic view  thazt doens't have a mode lso we do a breadcrumb manually
    template_name = "configuration/configuration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Configuration")
        context["title"] = _("Configuration")
        context["parent_url"] = reverse("core:configuration")
        return context


# ----------------------------------TAX----------------------------------


class ManageTaxHtmx(BaseManageHtmxFormView):
    form_class = TaxModelForm
    model = Tax
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class TaxDeleteHTMX(DeleteMixinHTMX):
    model = Tax


class TaxListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "core.view_tax"
    model = Tax

    template_name = "tables/table_partial.html"
    filterset_class = None
    table_class = TaxHTMxTable

    def get_queryset(self):
        return Tax.objects.all().order_by("name")


class ManageLeadSourceHtmx(BaseManageHtmxFormView):
    form_class = LeadSourceModelForm
    model = LeadSource
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class LeadSourceDeleteHTMX(DeleteMixinHTMX):
    model = LeadSource


class LeadSourceListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "core.view_leadsource"
    model = LeadSource

    template_name = "tables/table_partial.html"
    filterset_class = None  # Define your filterset class if needed
    table_class = LeadSourceHTMxTable  # Define your table class if needed

    def get_queryset(self):
        return LeadSource.objects.all().order_by("name")


# ----------------------------------Potential----------------------------------


class ManagePotentialHtmx(BaseManageHtmxFormView):
    permission_required = "core.add_potential"
    form_class = PotentialModelForm
    model = Potential
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class PotentialDeleteHTMX(DeleteMixinHTMX):
    permission_required = "core.delete_potential"
    model = Potential


class PotentialListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "core.view_potential"
    model = Potential

    template_name = "tables/table_partial.html"
    filterset_class = None  # Define your filterset class if needed
    table_class = PotentialHTMxTable  # Define your table class if needed

    def get_queryset(self):
        return Potential.objects.all()


class StatisticsView(PermissionRequiredMixin, TemplateView):
    permission_required = "transactions.can_view_statistique"
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_income_invoices = (
            ClientPayment.objects.aggregate(total_income=Sum("amount"))["total_income"]
            or 0
        )
        total_income_misc = (
            MiscTransaction.objects.filter(transaction_type="income").aggregate(
                total_income=Sum("amount")
            )["total_income"]
            or 0
        )
        total_income = total_income_invoices + total_income_misc
        context["total_income"] = total_income

        total_expence_staff = (
            StaffPayment.objects.aggregate(total_payment=Sum("amount"))["total_payment"]
            or 0
        )
        total_expence_misc = (
            MiscTransaction.objects.filter(transaction_type="expense").aggregate(
                total_expense=Sum("amount")
            )["total_expense"]
            or 0
        )
        total_expence = total_expence_staff + total_expence_misc
        context["total_expence"] = total_expence

        invoice_reste = sum(
            (inv.rest_amount for inv in Invoice.objects.all()), Decimal("0")
        )
        context["invoice_reste"] = invoice_reste
        print(f"invoice_reste----------->>>>: {invoice_reste}")

        return context
