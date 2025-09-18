import weasyprint
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from apps.billing.filters import BillFilterSet, InvoiceFilterSet, InvoiceFilterSet, QuoteFilterSet
from apps.billing.forms import (
    InvoiceItemModelFormSet,
    InvoiceModelForm,
    QuoteItemModelFormSet,
    QuoteModelForm,
)
from apps.billing.models import Bill, Invoice, Quote
from apps.billing.tables import BillHtmxTable, InvoiceHtmxTable, QuoteHtmxTable
from apps.business.models import BusinessSettings
from apps.core.mixins import (
    BaseManageHtmxFormView,
    BreadcrumbMixin,
    BulkDeleteMixinHTMX,
    DeleteMixinHTMX,
    ExportDataMixin,
    ImportDataMixin,
    TableImportFieldsMixin,
)
from apps.core.models import Tax

# ################################ Invoice Views ################################


class BillListView(BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "billing.view_invoice"
    model = Bill
    paginate_by = 10
    filterset_class = BillFilterSet


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["import_fields_url"] = reverse("billing:import_fields_invoice")
        
        context["model"] = self.model
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["bill_list.html"]


class QuoteListView(BillListView):
    permission_required = "billing.view_quote"
    model = Quote
    filterset_class = QuoteFilterSet
    table_class = QuoteHtmxTable

    def get_queryset(self):
        return Quote.objects.limit_user(self.request.user).all().order_by("-created_at")

class InvoiceListView(BillListView):
    model = Invoice
    filterset_class = InvoiceFilterSet
    table_class = InvoiceHtmxTable

    def get_queryset(self):
        return Invoice.objects.limit_user(self.request.user).all().order_by("-created_at")



class CompanyQuotesTable(QuoteListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = Quote.objects.filter(lead__company__pk=pk).order_by("-created_at")
        return queryset

    def get_table_kwargs(self):
        return {"company_pk": self.kwargs.get("pk")}



class CompanyInvoicesTable(InvoiceListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = Invoice.objects.filter(lead__company__pk=pk).order_by("-created_at")
        return queryset

    def get_table_kwargs(self):
        return {"company_pk": self.kwargs.get("pk")}



class ManageInvoiceHTMX(BaseManageHtmxFormView):
    form_class = InvoiceModelForm
    model = Invoice
    # parent_url_kwarg =  "lead_pk"
    parent_url_kwarg = ("company_pk", "lead_pk")
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_formsets(self):
        instance = self.get_object()
        print('instance:', instance)
        return {
            "invoice_items": InvoiceItemModelFormSet(
                self.request.POST or None, instance=instance, prefix="invoice_items"
            )
        }

class DeleteBulkBills(BulkDeleteMixinHTMX):
    model = Bill


class BillDetailView(BreadcrumbMixin, PermissionRequiredMixin, DetailView):
    permission_required = "billing.view_bill"
    model = Bill
    template_name = "bill_detail.html"
    context_object_name = "bill"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["business"] = BusinessSettings.objects.first()
        context["title"] = context["page_title"] =  self.object.get_bill_type_display() + " " + str(self.object.bill_number)
        context["parent_url"] = reverse(f"billing:list_{self.object.bill_type.lower()}")
        context["taxes"] = Tax.objects.filter(is_active=True)
        context["parent_page"] = self.object.get_bill_type_display()
        print('self.>>>>>>>>>>>>>>>>>>>>>>>>model', self.model)
        return context


class ImportInvoices(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "billing.add_invoice"
    model = Invoice
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
    ]

    def get_duplicate_check_fields(self):
        return []


class ImportFieldsInvoice(TableImportFieldsMixin, View):
    model = Invoice
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
    ]


class ExportInvoices(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "billing.view_invoice"
    model = Invoice
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
        "get_total_ttc",
        "get_total_net",
        "paid_amount",
        "rest_amount",
    ]


################################ Quotes Views ################################


@permission_required("billing.view_quote", raise_exception=True)
def print_bill_pdf(request, bill_id):

    bill = get_object_or_404(Bill, id=bill_id)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename={bill.bill_type}_{bill.bill_number}.pdf"
    business = BusinessSettings.objects.first()
    context = {
        "bill": bill,
        "business": business,
        "base_url": request.build_absolute_uri("/")[:-1],
    }
    if bill.is_invoice:
        context["taxes"] = Tax.objects.filter(is_active=True)
        template_name = "snippets/invoice_pdf.html"
    else:
        template_name = "snippets/bill_pdf.html"
        
    html = render_to_string(template_name, context)
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf(
        response,
    )
    return response
    # return HttpResponse(html)  
    

class ManageQuoteHTMX(BaseManageHtmxFormView):
    form_class = QuoteModelForm
    model = Quote
    parent_url_kwarg = ("company_pk", )

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_formsets(self):
        instance = self.get_object()
        return {
            "quote_items": QuoteItemModelFormSet(
                self.request.POST or None, instance=instance, prefix="quote_items"
            )
        }


class DeleteBill(DeleteMixinHTMX):
    model = Bill




class ImportQuotes(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "billing.add_quote"
    model = Quote
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
    ]

    def get_duplicate_check_fields(self):
        return []


class ImportFieldsQuote(TableImportFieldsMixin, View):
    model = Quote
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
    ]


class ExportQuotes(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "billing.view_quote"
    model = Quote
    fields = [
        "bill_number",
        "creation_date",
        "due_date",
        "state",
        "get_total_ttc",
        "get_total_net",
        "paid_amount",
        "rest_amount",
    ]


@permission_required("billing.add_invoice", raise_exception=True)
def convert_bill_to_invoice(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    invoice = bill.convert_to_invoice()

    message = _("Facture créée avec succès.")
    messages.success(request, str(message))
    return HttpResponseRedirect(
        reverse("billing:detail_bill", kwargs={"pk": invoice.id})
    )
