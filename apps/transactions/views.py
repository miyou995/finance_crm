from django.http import HttpResponse
from django.views import View
from apps.core.mixins import (
    BaseManageHtmxFormView,
    BreadcrumbMixin,
    BulkDeleteMixinHTMX,
    ChartMixin,
    DeleteMixinHTMX,
    ExportDataMixin,
)
from apps.crm.models.contact import Contact
from .forms import (
    ExpenseModelForm,
    IncomeModelForm,
    BillPaiementModelForm,
    StaffPaymentModelForm,
)
import weasyprint

from django_tables2 import SingleTableMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView
from .models import (
    Expense,
    Income,
    ClientPayment,
    LedgerEntry,
    StaffPayment,
    MiscTransaction,
)
from .tables import (
    ClientPaymentHTMxTable,
    LedgerEntryTable,
    StaffPaymentHTMxTable,
    AutreTransactionTableHTMxTable,
)
from .filters import (
    ClientPaymentFilter,
    LedgerEntryFilter,
    StaffPaymentsFilter,
    AutreTransactionFilter,
)
from django.db.models import Sum, F, DecimalField, Q

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import ExpressionWrapper

User = get_user_model()



######################### INVOICES VIEWS #########################



# tables views
class InvoicesPaymentView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "transactions.view_clientpayment"
    table_class = ClientPaymentHTMxTable
    filterset_class = ClientPaymentFilter
    paginate_by = 15
    model = ClientPayment

    def get_queryset(self):
        queryset = ClientPayment.objects.select_related(
            "bill", "created_by", "updated_by"
        ).order_by("-created_at")
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_url"] = self.get_queryset().model.get_list_url()
        total_payments = self.filterset.qs.aggregate(total=Sum("amount")).get(
            "total", 0
        )
        context["total"] = total_payments
        context["total_income"] = total_payments
        context["total_expense"] = 0
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["create_url"] = self.get_queryset().model.get_create_url()
        context["export_url"] = self.model.get_export_url()
        context["has_perms"] = self.request.user.has_perm("transactions.add_clientpayment")
        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "transactions.html"
        return template_name


class CompanyInvoicesPaymentTable(InvoicesPaymentView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = ClientPayment.objects.filter(
            Q(bill__lead__company__pk=pk ) | Q(client__pk=pk)
        ).order_by("-created_at")
        return queryset

    def get_table_kwargs(self):
        return {"company_pk": self.kwargs.get("pk")}


class ManageInvoicePaiementHtmx(BaseManageHtmxFormView):
    permission_required = "transactions.add_clientpayment"
    form_class = BillPaiementModelForm
    model = ClientPayment
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
        "update_total": None,
    }


class CreateCompanyInvoicePaiment(ManageInvoicePaiementHtmx):
    parent_url_kwarg = ("company_pk",)

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['company_pk'] = self.kwargs.get('company_pk')
    #     return kwargs


class CreateInvoiceClientPayment(ManageInvoicePaiementHtmx):
    parent_url_kwarg = ("bill_pk",)


class DeleteInvoicePaiement(DeleteMixinHTMX):
    model = ClientPayment


class DeleteBulkClientPayments(BulkDeleteMixinHTMX):
    model = ClientPayment


class ExportClientPayment(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "transactions.view_clientpayment"
    model = ClientPayment
    fields = [
        "bill",
        "amount",
        "rest_amount",
        "notes",
        "date",
    ]



# --------------------------------------- staff-------------------------------------------------
class StaffPaymentView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "transactions.view_staffpayment"
    table_class = StaffPaymentHTMxTable
    paginate_by = 15
    model = StaffPayment
    filterset_class = StaffPaymentsFilter

    def get_queryset(self):
        queryset = StaffPayment.objects.select_related(
            "staff_member", "created_by"
        ).order_by("-created_at")
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_url"] = self.get_queryset().model.get_list_url()
        context["create_url"] = self.get_queryset().model.get_create_url()
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["export_url"] = self.model.get_export_url()
        context["has_perms"] = self.request.user.has_perm(
            "transactions.add_staffpayment"
        )
        context["list_url"] = self.get_queryset().model.get_list_url()
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["transactions.html"]


class ManageStaffPaymentHtmx(BaseManageHtmxFormView):
    form_class = StaffPaymentModelForm
    model = StaffPayment
    # parent_url_kwarg = 'staff_member_pk'

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
        "update_total": None,
    }


class StaffPaymentDeleteHTMX(DeleteMixinHTMX):
    model = StaffPayment
    htmx_additional_event = "refresh_table"


class StaffPaymentDeleteBulk(BulkDeleteMixinHTMX):
    model = StaffPayment


class ExportStaffPayment(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "transactions.view_staffpayment"
    model = StaffPayment
    fields = [
        "staff_member",
        "amount",
        "notes",
        "date",
    ]


# --------------------------------------- DIVERS TRANSACTION --------------------------------------------


class AutreTransactionView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "transactions.view_misctransaction"
    table_class = AutreTransactionTableHTMxTable
    filterset_class = AutreTransactionFilter
    paginate_by = 20
    model = MiscTransaction

    def get_queryset(self):
        queryset = MiscTransaction.objects.select_related("contact")
        contact_pk = self.kwargs.get("contact_pk")
        if contact_pk:
            contact = get_object_or_404(Contact, pk=contact_pk)
            queryset = queryset.filter(contact=contact)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_url"] = self.get_queryset().model.get_list_url()
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["export_url"] = self.model.get_export_url()
        filtered_qs = self.filterset.qs

        total_revenu = (
            filtered_qs.filter(transaction_type="income").aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        total_expense = (
            filtered_qs.filter(transaction_type="expense").aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        result = total_revenu - total_expense

        context["total"] = result
        context["total_income"] = total_revenu
        context["total_expense"] = total_expense

        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "misc-transactions.html"
        return template_name



class ManageAutreTransactionHtmx(BaseManageHtmxFormView):
    form_class = IncomeModelForm
    model = MiscTransaction

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
        "update_total": None,
    }


class ManageIncomeHtmx(ManageAutreTransactionHtmx):
    model = Income
    parent_url_kwarg = ("contact_pk",)


class ManageExpenseHtmx(ManageIncomeHtmx):
    model = Expense
    form_class = ExpenseModelForm


class AutreTransactionDelete(DeleteMixinHTMX):
    model = MiscTransaction
    htmx_additional_event = "refresh_table_transactions_table"


class AutreTransactionDeleteBulk(BulkDeleteMixinHTMX):
    model = MiscTransaction


class ExportAutreTransaction(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "transactions.view_misctransaction"
    model = MiscTransaction
    fields = [
        "title",
        "contact",
        "amount",
        "notes",
        "date",
        "transaction_type",
    ]


class StatisticClientPaymentPerMonth(ChartMixin):
    model = ClientPayment
    field_to_aggregate = "invoice_remaining_amount"   # <-- add this
    permission = "transactions.can_view_chiffre_affaire"
    chart_id = "invoiceChart"
    chart_title = "Chiffre d'affaire par mois des Factures"
    date_field = "date"
    chart_type = "pie"
    aggregate_function = Sum  # ensure Sum is used

    def get_queryset(self):
        qs = super().get_queryset().select_related('bill')
        # annotate a DB expression for remaining amount per payment (works for aggregation)
        qs = qs.annotate(
            invoice_remaining_amount=ExpressionWrapper(
                F('invoice_rest_amount') - F('invoice_paid_amount'),
                output_field=DecimalField(max_digits=11, decimal_places=2),
            )
        )
        return qs




def impression_resu_autre_transaction(request, transaction_id):
    transaction = get_object_or_404(MiscTransaction, id=transaction_id)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=paiement_{transaction.id}.pdf"
    context = {
        "transaction": transaction,
    }
    html = render_to_string("snippets/autre_transaction_2recu_pdf.html", context)
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        response
    )
    return response


class LedgerView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "transactions.view_ledgerentry"
    table_class = LedgerEntryTable
    filterset_class = LedgerEntryFilter
    paginate_by = 20

    def get_queryset(self):
        queryset = LedgerEntry.objects.select_related(
            "client_payment",
            "staff_payment",
            "misc_transaction",
        )
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_ledger_url"] = True
        context["export_url"] = LedgerEntry.get_export_url()
        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "transactions.html"
        return template_name

class ManageLedgerEntry(BaseManageHtmxFormView):
    model = LedgerEntry
    htmx_additional_event = "refresh_table"

class DeleteLedgerEntry(DeleteMixinHTMX):
    model = LedgerEntry
    htmx_additional_event = "refresh_table"

class ExportLedgerView(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "transactions.view_ledgerentry"
    model = LedgerEntry
    fields = [
        "client_payment",
        "staff_payment",
        "misc_transaction",
        "entry_type",
        "amount",
        "created_by",
        "date",
    ]




