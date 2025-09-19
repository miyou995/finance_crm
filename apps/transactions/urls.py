from django.urls import path


from .views import (
    AutreTransactionDeleteBulk,
    CompanyInvoicesPaymentTable,
    CreateCompanyInvoicePaiment,
    CreateInvoiceClientPayment,
    DeleteBulkClientPayments,
    DeleteInvoicePaiement,
    DeleteLedgerEntry,
    ExportAutreTransaction,
    ExportClientPayment,
    ExportLedgerView,
    ExportStaffPayment,
    ManageAutreTransactionHtmx,
    ManageExpenseHtmx,
    ManageIncomeHtmx,
    ManageInvoicePaiementHtmx,
    ManageLedgerEntry,
    ManageStaffPaymentHtmx,
    StaffPaymentDeleteBulk,
    StaffPaymentDeleteHTMX,
    StaffPaymentView,
    StatisticClientPaymentPerMonth,
    impression_resu_autre_transaction,
    CreateCompanyQuotePayment,
    AutreTransactionView,
    ManageQuotePaiementHtmx,
    AutreTransactionDelete,
    InvoicesPaymentView,
    LedgerView,
)


app_name = "transactions"


urlpatterns = [
    # Counters



    path(
        "statistic_client_payment_per_month/",
        StatisticClientPaymentPerMonth.as_view(),
        name="statistic_client_payment_per_month",
    ),

    # 	ClientPayment
    path(
        "paiements/invoices/", InvoicesPaymentView.as_view(), name="list_clientpayment"
    ),
    # ClientPayment for company
    path(
        "paiements/invoices/create",
        ManageInvoicePaiementHtmx.as_view(),
        name="create_clientpayment",
    ),
    path(
        "paiements/quotes/create",
        ManageQuotePaiementHtmx.as_view(),
        name="create_quote_payment",
    ),
    path(
        "paiements/invoices/company/create/<int:company_pk>/",
        CreateCompanyInvoicePaiment.as_view(),
        name="create_company_clientpayment",
    ),
        path(
        "paiements/quotes/company/create/<int:company_pk>/",
        CreateCompanyQuotePayment.as_view(),
        name="create_company_quote_payment",
    ),
    
    path(
        "paiements/invoices/invoice/create/<int:bill_pk>/",
        CreateInvoiceClientPayment.as_view(),
        name="create_bill_clientpayment",
    ),
    # ClientPayment for invoice
    path(
        "paiements/bills/bill/<int:bill_pk>/",
        CreateInvoiceClientPayment.as_view(),
        name="create_invoice_clientpayment",
    ),
    path(
        "invoices-paiements/<int:pk>/update",
        ManageInvoicePaiementHtmx.as_view(),
        name="update_clientpayment",
    ),
    path(
        "invoices-paiements/<int:pk>/delete",
        DeleteInvoicePaiement.as_view(),
        name="delete_clientpayment",
    ),
    path(
        "invoices-paiements/bulk-delete",
        DeleteBulkClientPayments.as_view(),
        name="bulk_delete_clientpayment",
    ),
    path(
        "paiements/company/<int:pk>/",
        CompanyInvoicesPaymentTable.as_view(),
        name="company_invoices_payment",
    ),
    path(
        "export/invoicepayment/",
        ExportClientPayment.as_view(),
        name="export_clientpayment",
    ),
    # 	Paiement
    
    #   staff remuneration
    path(
        "remunerations_staff/",
        StaffPaymentView.as_view(),
        name="list_staffpayment",
    ),
    path(
        "remunerations_staff/create/",
        ManageStaffPaymentHtmx.as_view(),
        name="create_staffpayment",
    ),
    path(
        "remunerations_staff/update/<int:pk>",
        ManageStaffPaymentHtmx.as_view(),
        name="update_staffpayment",
    ),
    # path('remunerations_staff/create/<int:staff_member_pk>', ManageStaffPaymentHtmx.as_view(), name='create_staff_remuneration'), # Not used
    path(
        "remunerations_staff/delete/<int:pk>",
        StaffPaymentDeleteHTMX.as_view(),
        name="delete_staffpayment",
    ),
    path(
        "remunerations_staff/bulk_delete_staffpayment/",
        StaffPaymentDeleteBulk.as_view(),
        name="bulk_delete_staffpayment",
    ),
    path(
        "remunerations_staff/export_staffpayment/",
        ExportStaffPayment.as_view(),
        name="export_staffpayment",
    ),
    # Expense
    path(
        "transaction-expense/create", ManageExpenseHtmx.as_view(), name="create_expense"
    ),
    path(
        "transaction-expense/create/<str:contact_pk>",
        ManageExpenseHtmx.as_view(),
        name="create_contact_expense",
    ),
    path("transaction-income/create", ManageIncomeHtmx.as_view(), name="create_income"),
    path(
        "transaction-income/create/<str:contact_pk>",
        ManageIncomeHtmx.as_view(),
        name="create_contact_income",
    ),
    path(
        "transaction/create_autre",
        ManageAutreTransactionHtmx.as_view(),
        name="create_misctransaction",
    ),
    path(
        "transaction/update_misctransaction/<int:pk>",
        ManageAutreTransactionHtmx.as_view(),
        name="update_misctransaction",
    ),
    path(
        "transaction-income/delete/<int:pk>",
        AutreTransactionDelete.as_view(),
        name="delete_misctransaction",
    ),
    path(
        "transaction/misctransactions/list",
        AutreTransactionView.as_view(),
        name="list_misctransaction",
    ),
    path(
        "transaction/misctransactions/list/contact/<int:contact_pk>",
        AutreTransactionView.as_view(),
        name="list_contact_misctransaction",
    ),
    path(
        "transaction/export_misctransaction/",
        ExportAutreTransaction.as_view(),
        name="export_misctransaction",
    ),
    path(
        "transaction/bulk_delete_misctransaction/",
        AutreTransactionDeleteBulk.as_view(),
        name="bulk_delete_misctransaction",
    ),
    # Deleteview

    path(
        "transaction/impression_resu_autre_transaction/<int:transaction_id>",
        impression_resu_autre_transaction,
        name="impression_resu_autre_transaction",
    ),
    ####### Ledger
    path("transaction/ledger", LedgerView.as_view(), name="ledger_entry"),
    path("transaction/export_ledger", ExportLedgerView.as_view(), name="export_ledger"),
    path("transactions/ledgerentry/create/", ManageLedgerEntry.as_view(), name="create_ledgerentry"),
    path("transactions/ledgerentry/update/<int:pk>/", ManageLedgerEntry.as_view(), name="update_ledgerentry"),
    path("transactions/delete_ledgerentry/<int:pk>/", DeleteLedgerEntry.as_view(), name="delete_ledgerentry"),
]
