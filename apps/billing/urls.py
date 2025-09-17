from django.urls import path
from apps.billing.views import (
    InvoiceListView,
    ManageInvoiceHTMX,
    DeleteInvoice,
    DeleteBulkInvoices,
    InvoiceDetailView,
    CompanyInvoicesTable,
    ExportInvoices,
    ImportInvoices,
    ImportFieldsInvoice,
    QuoteListView,
    CompanyQuotesTable,
    ManageQuoteHTMX,
    DeleteQuote,
    DeleteBulkQuotes,
    QuoteDetailView,
    ExportQuotes,
    ImportQuotes,
    ImportFieldsQuote,
    print_invoice_pdf,
    print_quote_pdf,
    convert_quote_to_invoice,
)

app_name = "billing"


urlpatterns = [
    ################ Invoices ################
    path("invoices/", InvoiceListView.as_view(), name="list_invoice"),
    path("invoices/create/", ManageInvoiceHTMX.as_view(), name="create_invoice"),
    path(
        "invoices/create/<int:company_pk>/",
        ManageInvoiceHTMX.as_view(),
        name="create_company_invoice",
    ),
    path(
        "invoices/<int:pk>/update/", ManageInvoiceHTMX.as_view(), name="update_invoice"
    ),
    path("invoices/<int:pk>/delete/", DeleteInvoice.as_view(), name="delete_invoice"),
    path("invoices/bulk-delete/",DeleteBulkInvoices.as_view(),name="bulk_delete_invoices",),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="detail_invoice"),
    path("invoices/print_invoice_pdf/<int:invoice_id>/",print_invoice_pdf,name="print_invoice_pdf",),
    path("invoices/company/<int:pk>/",CompanyInvoicesTable.as_view(),name="company_invoices",),
    path("invoices/export/", ExportInvoices.as_view(), name="export_invoices"),
    path("invoices/import/", ImportInvoices.as_view(), name="import_invoices"),
    path("invoices/import-fields/",ImportFieldsInvoice.as_view(),name="import_fields_invoice",),
    ############## Quotes ################
    path("quotes/", QuoteListView.as_view(), name="list_quote"),
    path("quotes/company/<int:pk>/", CompanyQuotesTable.as_view(), name="company_quotes"),
    path("quotes/create/", ManageQuoteHTMX.as_view(), name="create_quote"),
    path("quotes/create/<int:company_pk>/",ManageQuoteHTMX.as_view(),name="create_company_quote",),
    path("quotes/<int:pk>/update/", ManageQuoteHTMX.as_view(), name="update_quote"),
    path("quotes/<int:pk>/delete/", DeleteQuote.as_view(), name="delete_quote"),
    path("quotes/bulk-delete/", DeleteBulkQuotes.as_view(), name="bulk_delete_quotes"),
    path("quotes/<int:pk>/", QuoteDetailView.as_view(), name="detail_quote"),
    path("quotes/print_quote_pdf/<int:quote_id>/",print_quote_pdf,name="print_quote_pdf",),
    path("quotes/convert/<int:quote_id>/",convert_quote_to_invoice,name="convert_quote_to_invoice",),
    path("quotes/export/", ExportQuotes.as_view(), name="export_quotes"),
    path("quotes/import/", ImportQuotes.as_view(), name="import_quotes"),
    path("quotes/import-fields/", ImportFieldsQuote.as_view(), name="import_fields_quote"),
]
