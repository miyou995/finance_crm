from django.urls import path
from apps.billing.views import (
    DeleteBulkBills,
    InvoiceListView,
    ManageInvoiceHTMX,
    
    BillDetailView,
    CompanyInvoicesTable,
    ExportInvoices,
    ImportInvoices,
    ImportFieldsInvoice,
    QuoteListView,
    CompanyQuotesTable,
    ManageQuoteHTMX,
    DeleteBill,
    ExportQuotes,
    ImportQuotes,
    ImportFieldsQuote,
    print_bill_pdf,
    convert_bill_to_invoice,
)

app_name = "billing"


urlpatterns = [
    ################ Invoices ################
    path("invoices/", InvoiceListView.as_view(), name="list_invoice"),
    path("invoices/create/", ManageInvoiceHTMX.as_view(), name="create_invoice"),
    path("invoices/company/create/<int:company_pk>/",ManageInvoiceHTMX.as_view(),name="create_company_invoice",),
    path("invoices/lead/create/<int:lead_pk>/",ManageInvoiceHTMX.as_view(),name="create_lead_invoice",),
    path(
        "invoices/update/<int:pk>/", ManageInvoiceHTMX.as_view(), name="update_invoice" # TODO DELETE
    ),
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
    path("bills/bulk-delete/",DeleteBulkBills.as_view(),name="bulk_delete_bills",),
    path("bills/<int:pk>/", BillDetailView.as_view(), name="detail_bill"),
    path("bills/<int:pk>/delete/", DeleteBill.as_view(), name="delete_bill"),
    path("quotes/print_quote_pdf/<int:bill_id>/",print_bill_pdf,name="print_bill_pdf",),
    path("quotes/convert/<int:bill_id>/",convert_bill_to_invoice,name="convert_bill_to_invoice",),
    path("quotes/export/", ExportQuotes.as_view(), name="export_quotes"),
    path("quotes/import/", ImportQuotes.as_view(), name="import_quotes"),
    path("quotes/import-fields/", ImportFieldsQuote.as_view(), name="import_fields_quote"),
]
