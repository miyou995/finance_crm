import ssl
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView
import weasyprint
from apps.billing.filters import InvoiceFilterSet, QuoteFilterSet
from apps.billing.forms import (
    InvoiceItemModelFormSet,
    InvoiceModelForm,
    QuoteItemModelFormSet,
    QuoteModelForm,
)
from apps.billing.models import Invoice, Quote
from apps.billing.tables import InvoiceHtmxTable, QuoteHtmxTable
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
from django.template.loader import render_to_string
from django.contrib import messages
from apps.core.models import Tax
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required

# ################################ Invoice Views ################################


@permission_required("billing.view_invoice", raise_exception=True)
def print_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=facture_{invoice.id}.pdf"
    context = {
        "invoice": invoice,
        "business": BusinessSettings.objects.first(),
        "invoice_items": invoice.lines.all(),
        "taxes": Tax.objects.filter(is_active=True),
    }
    html = render_to_string("snippets/invoice_pdf.html", context)
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        response
    )
    return response


class InvoiceListView(BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "billing.view_invoice"
    model = Invoice
    table_class = InvoiceHtmxTable
    paginate_by = 10
    filterset_class = InvoiceFilterSet

    def get_queryset(self):
        queryset = (
            Invoice.objects.limit_user(self.request.user).all().order_by("-created_at")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["import_fields_url"] = reverse("billing:import_fields_invoice")
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["invoice_list.html"]


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
    parent_url_kwarg = "company_pk"
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_formsets(self):
        instance = self.get_object()
        return {
            "invoice_items": InvoiceItemModelFormSet(
                self.request.POST or None, instance=instance, prefix="invoice_items"
            )
        }


class DeleteInvoice(DeleteMixinHTMX):
    model = Invoice


class DeleteBulkInvoices(BulkDeleteMixinHTMX):
    model = Invoice


class InvoiceDetailView(BreadcrumbMixin, PermissionRequiredMixin, DetailView):
    permission_required = "billing.view_invoice"
    model = Invoice
    template_name = "invoice_detail.html"
    context_object_name = "invoice"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["business"] = BusinessSettings.objects.first()
        context["invoice_items"] = self.object.lines.all()
        context["taxes"] = Tax.objects.filter(is_active=True)
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
def print_quote_pdf(request, quote_id):
    import logging
    logger = logging.getLogger('weasyprint')
    # logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))
    logger.addHandler(logging.FileHandler('weasyprint.log'))
    from PIL import features
    print("WebP:", features.check("webp"))

    quote = get_object_or_404(Quote, id=quote_id)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=devis_{quote.id}.pdf"
    business = BusinessSettings.objects.first()
    context = {
        "quote": quote,
        "logo_url": business.logo.url,
        "base_url": request.build_absolute_uri("/")[:-1],
        "business": business,
        "quote_items": quote.lines.all(),
    }
    html = render_to_string("snippets/quote_pdf.html", context)
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf(
        response,
    )
    return response
    # return HttpResponse(html)  

class QuoteListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "billing.view_quote"
    model = Quote
    table_class = QuoteHtmxTable
    paginate_by = 10
    filterset_class = QuoteFilterSet

    def get_queryset(self):
        return Quote.objects.limit_user(self.request.user).all().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["import_fields_url"] = reverse("billing:import_fields_quote")
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["quote_list.html"]


class CompanyQuotesTable(QuoteListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = Quote.objects.filter(lead__company__pk=pk).order_by("-created_at")
        return queryset

    def get_table_kwargs(self):
        return {"company_pk": self.kwargs.get("pk")}


class ManageQuoteHTMX(BaseManageHtmxFormView):
    form_class = QuoteModelForm
    model = Quote
    parent_url_kwarg = "company_pk"

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
        
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["size_class"] = "modal-fullscreen"
    #     return context

class DeleteQuote(DeleteMixinHTMX):
    model = Quote


class DeleteBulkQuotes(BulkDeleteMixinHTMX):
    model = Quote


class QuoteDetailView(BreadcrumbMixin, PermissionRequiredMixin, DetailView):
    permission_required = "billing.view_quote"
    model = Quote
    template_name = "quote_detail.html"
    context_object_name = "quote"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-950px"
        context["business"] = BusinessSettings.objects.first()
        context["quote_items"] = self.object.lines.all()
        context["taxes"] = Tax.objects.filter(is_active=True)
        return context


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
def convert_quote_to_invoice(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    invoice = quote.convert_to_invoice()
    items = quote.lines.all()
    items = [item.convert_to_invoice_item(invoice) for item in items]
    message = "Devis converti en facture avec succès."
    messages.success(request, str(message))
    return HttpResponseRedirect(
        reverse("billing:detail_invoice", kwargs={"pk": invoice.id})
    )
