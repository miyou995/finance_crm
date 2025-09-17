from django.urls import path
from apps.crm.views import (
    ContactListView,
    ManageContactHTMX,
    DeleteContact,
    DeleteBulkContacts,
    ImportContacts,
    ExportContacts,
    ContactDetailView,
    ImportFieldsContact,
    CompanyListView,
    CompanyFinancialInfo,
    ManageCompanyHTMX,
    DeleteCompany,
    ImportCompanies,
    ImportFieldsCompanies,
    ExportCompanies,
    DeleteBulkCompanies,
    CompanyDetailView,
    CompanyChartView,
    CompanyContactsTable,
    ManageCompanyDocumentHTMX,
    DeleteCompanyDocument,
    ActivitySectorListView,
    ManageActivitySectorHTMX,
    DeleteActivitySector,
    ManagePublicForm,
    thank_you_view,
)

app_name = "crm"

urlpatterns = [
    ########## CONTACT #############
    path("contacts/", ContactListView.as_view(), name="list_contact"),
    path("contacts/create/", ManageContactHTMX.as_view(), name="create_contact"),
    path(
        "contacts/update/<int:pk>/", ManageContactHTMX.as_view(), name="update_contact"
    ),
    ##contact for company
    path(
        "contacts/company_contacts/<int:company_pk>/",
        ManageContactHTMX.as_view(),
        name="create_company_contacts",
    ),
    path("contacts/delete/<int:pk>/", DeleteContact.as_view(), name="delete_contact"),
    path(
        "contacts/bulk-delete/",
        DeleteBulkContacts.as_view(),
        name="bulk_delete_contacts",
    ),
    path("contacts/import/", ImportContacts.as_view(), name="import_contact"),
    path("contacts/export/", ExportContacts.as_view(), name="export_contact"),
    path("contacts/<int:pk>/", ContactDetailView.as_view(), name="detail_contact"),
    path(
        "contacts/import-fields/",
        ImportFieldsContact.as_view(),
        name="import_fields_contact",
    ),
    ########## COMPANY #############
    path("companies/", CompanyListView.as_view(), name="list_company"),
    path("companies/create/", ManageCompanyHTMX.as_view(), name="create_company"),
    path(
        "companies/update/company_financial/<int:pk>/",
        CompanyFinancialInfo.as_view(),
        name="update_company_financial",
    ),
    path(
        "companies/update/<int:pk>/", ManageCompanyHTMX.as_view(), name="update_company"
    ),
    path("companies/delete/<int:pk>/", DeleteCompany.as_view(), name="delete_company"),
    path("companies/import/", ImportCompanies.as_view(), name="import_company"),
    path(
        "companies/import-fields/",
        ImportFieldsCompanies.as_view(),
        name="import_fields_company",
    ),
    path("companies/export/", ExportCompanies.as_view(), name="export_company"),
    path(
        "companies/bulk-delete/",
        DeleteBulkCompanies.as_view(),
        name="bulk_delete_companies",
    ),
    path(
        "companies/detail/<int:pk>/", CompanyDetailView.as_view(), name="detail_company"
    ),
    path(
        "companies/detail/charts/<int:pk>/",
        CompanyChartView.as_view(),
        name="charts_company",
    ),
    path(
        "companies/company_contacts/<int:pk>/",
        CompanyContactsTable.as_view(),
        name="company_contacts",
    ),
    ######## document #############
    path(
        "companies/create_companydocument/<int:company_pk>/",
        ManageCompanyDocumentHTMX.as_view(),
        name="create_companydocument",
    ),
    path(
        "companies/document/<int:pk>/delete/",
        DeleteCompanyDocument.as_view(),
        name="delete_companydocument",
    ),
    ################ Activity Sector #############
    path(
        "activity-sectors/",
        ActivitySectorListView.as_view(),
        name="list_activitysector",
    ),
    path(
        "activity-sectors/create/",
        ManageActivitySectorHTMX.as_view(),
        name="create_activitysector",
    ),
    path(
        "activity-sectors/update/<int:pk>/",
        ManageActivitySectorHTMX.as_view(),
        name="update_activitysector",
    ),
    path(
        "activity-sectors/delete/<int:pk>/",
        DeleteActivitySector.as_view(),
        name="delete_activitysector",
    ),
    path(
        "public-forms/",
        ManagePublicForm.as_view(),
        name="public_forms_url",
    ),
    path('thank_you/', thank_you_view, name='thank_you_view'),

]
