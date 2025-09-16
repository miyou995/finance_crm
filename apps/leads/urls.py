from django.urls import path


from apps.leads.views import (
ChangeStateView,
ChangeB2CStateView,
B2BLeadStateUserView,
B2CLeadStateUserView,
B2BLeadDetailView,
B2CLeadDetailView,
ManageB2bLeadHTMX,
DeleteB2bLead,
DeleteBulkB2bLeads,
CompanyB2bLeadsTable,
ImportB2bLead,
ExportB2bLead,
ImportFieldsB2bLead,
ManageB2cLeadHTMX,
DeleteB2cLead,
DeleteBulkB2cLeads,
ContactB2cLeadsTable,
ImportB2cLead,
ExportB2cLead,
B2bLeadListView,
B2cLeadListView,
NewB2bLeadListView,
NewB2cLeadListView,
UntreatedB2bLeadListView,
UntreatedB2cLeadListView,
DuplicatedB2bLeadListView,
DuplicatedB2cLeadListView,
NonInteresseB2bLeadListView,
NonInteresseB2cLeadListView,
QualifiedB2bLeadListView,
QualifiedB2cLeadListView,
InjoignableB2bLeadListView,
InjoignableB2cLeadListView,
NonQualifiedB2bLeadListView,
NonQualifiedB2cLeadListView,
LostB2bLeadListView,
LostB2cLeadListView,
CompletedB2bLeadListView,
CompletedB2cLeadListView,
)


app_name = "leads"


urlpatterns = [
    path(
        "lead/<int:lead_pk>/change_b2b_state/<int:target_state>/",
        ChangeStateView.as_view(),
        name="change_b2blead_state",
    ),
    path(
        "lead/<int:lead_pk>/change_b2c_state/<int:target_state>/",
        ChangeB2CStateView.as_view(),
        name="change_b2clead_state",
    ),
    ############## LEAD STATE VIEWS ##############
    path(
        "leadstates/b2b/user/<int:pk>/",
        B2BLeadStateUserView.as_view(),
        name="user_b2blead_state",
    ),
    path(
        "leadstates/b2c/user/<int:pk>/",
        B2CLeadStateUserView.as_view(),
        name="user_b2clead_state",
    ),
    path("leads/list_lead/", B2bLeadListView.as_view(), name="list_lead"),
    path(
        "leads/detail_b2blead/<int:pk>/",
        B2BLeadDetailView.as_view(),
        name="detail_b2blead",
    ),
    path(
        "leads/detail_b2clead/<int:pk>/",
        B2CLeadDetailView.as_view(),
        name="detail_b2clead",
    ),
    ########## B2B LEAD #############
    path("leads/create_b2b_lead/", ManageB2bLeadHTMX.as_view(), name="create_b2blead"),
    path(
        "leads/update_b2b_lead/<int:pk>/",
        ManageB2bLeadHTMX.as_view(),
        name="update_b2blead",
    ),
    path(
        "leads/create_b2b_lead/<int:company_pk>/",
        ManageB2bLeadHTMX.as_view(),
        name="create_company_b2blead",
    ),
    path(
        "leads/delete_b2b_lead/<int:pk>/",
        DeleteB2bLead.as_view(),
        name="delete_b2blead",
    ),
    path(
        "leads/bulk_delete_b2b_leads/",
        DeleteBulkB2bLeads.as_view(),
        name="bulk_delete_b2b_leads",
    ),
    path(
        "leads/company_leads/<int:pk>/",
        CompanyB2bLeadsTable.as_view(),
        name="company_leads",
    ),
    path("leads/import_b2b_lead/", ImportB2bLead.as_view(), name="import_b2b_lead"),
    path("leads/export_b2b_lead/", ExportB2bLead.as_view(), name="export_b2b_lead"),
    path(
        "leads/import-fields-b2b/",
        ImportFieldsB2bLead.as_view(),
        name="import_fields_b2b_lead",
    ),
    ########## B2C LEAD #############
    path("leads/create_b2c_lead/", ManageB2cLeadHTMX.as_view(), name="create_b2clead"),
    path(
        "leads/create_b2c_lead/<int:contact_pk>/",
        ManageB2cLeadHTMX.as_view(),
        name="create_contact_b2clead",
    ),
    path(
        "leads/update_b2c_lead/<int:pk>/",
        ManageB2cLeadHTMX.as_view(),
        name="update_b2clead",
    ),
    path(
        "leads/delete_b2c_lead/<int:pk>/",
        DeleteB2cLead.as_view(),
        name="delete_b2clead",
    ),
    path(
        "leads/bulk_delete_b2c_leads/",
        DeleteBulkB2cLeads.as_view(),
        name="bulk_delete_b2c_leads",
    ),
    path(
        "leads/contact_leads/<int:pk>/",
        ContactB2cLeadsTable.as_view(),
        name="contact_leads",
    ),
    path("leads/import_b2c_lead/", ImportB2cLead.as_view(), name="import_b2c_lead"),
    path("leads/export_b2c_lead/", ExportB2cLead.as_view(), name="export_b2c_lead"),
    path("leads/b2b_list/", B2bLeadListView.as_view(), name="all_b2b_lead_list"),
    path("leads/b2c_list/", B2cLeadListView.as_view(), name="all_b2c_lead_list"),
    # path('leads/user-b2blead-list/<int:pk>/', UserB2BLeadsTable.as_view(), name='user_b2b_lead_list'),
    # path('leads/user-b2clead-list/<int:pk>/', UserB2CLeadsTable.as_view(), name='user_b2c_lead_list'),
    ############### LEAD STATUS ##############
    path(
        "leads/new_b2b_lead_list/",
        NewB2bLeadListView.as_view(),
        name="new_b2b_lead_list",
    ),
    path(
        "leads/new_b2c_lead_list/",
        NewB2cLeadListView.as_view(),
        name="new_b2c_lead_list",
    ),
    path(
        "leads/untreated_b2b_lead_list/",
        UntreatedB2bLeadListView.as_view(),
        name="untreated_b2b_lead_list",
    ),
    path(
        "leads/untreated_b2c_lead_list/",
        UntreatedB2cLeadListView.as_view(),
        name="untreated_b2c_lead_list",
    ),
    path(
        "leads/duplicated_b2b_lead_list/",
        DuplicatedB2bLeadListView.as_view(),
        name="duplicated_b2b_lead_list",
    ),
    path(
        "leads/duplicated_b2c_lead_list/",
        DuplicatedB2cLeadListView.as_view(),
        name="duplicated_b2c_lead_list",
    ),
    path(
        "leads/non_interesse_b2b_lead_list/",
        NonInteresseB2bLeadListView.as_view(),
        name="non_interesse_b2b_lead_list",
    ),
    path(
        "leads/non_interesse_b2c_lead_list/",
        NonInteresseB2cLeadListView.as_view(),
        name="non_interesse_b2c_lead_list",
    ),
    path(
        "leads/qualified_b2b_lead_list/",
        QualifiedB2bLeadListView.as_view(),
        name="qualified_b2b_lead_list",
    ),
    path(
        "leads/qualified_b2c_lead_list/",
        QualifiedB2cLeadListView.as_view(),
        name="qualified_b2c_lead_list",
    ),
    path(
        "leads/injoignable_b2b_lead_list/",
        InjoignableB2bLeadListView.as_view(),
        name="injoignable_b2b_lead_list",
    ),
    path(
        "leads/injoignable_b2c_lead_list/",
        InjoignableB2cLeadListView.as_view(),
        name="injoignable_b2c_lead_list",
    ),
    path(
        "leads/non_qualified_b2b_lead_list/",
        NonQualifiedB2bLeadListView.as_view(),
        name="non_qualified_b2b_lead_list",
    ),
    path(
        "leads/non_qualified_b2c_lead_list/",
        NonQualifiedB2cLeadListView.as_view(),
        name="non_qualified_b2c_lead_list",
    ),
    path(
        "leads/lost_b2b_lead_list/",
        LostB2bLeadListView.as_view(),
        name="lost_b2b_lead_list",
    ),
    path(
        "leads/lost_b2c_lead_list/",
        LostB2cLeadListView.as_view(),
        name="lost_b2c_lead_list",
    ),
    path(
        "leads/completed_b2b_lead_list/",
        CompletedB2bLeadListView.as_view(),
        name="completed_b2b_lead_list",
    ),
    path(
        "leads/completed_b2c_lead_list/",
        CompletedB2cLeadListView.as_view(),
        name="completed_b2c_lead_list",
    ),
]
