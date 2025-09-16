from django.urls import path
from .views import (
                    IndexView,
                    ConfigugrationView,
                    StatisticsView,
                    TaxListView,
                    ManageTaxHtmx,
                    TaxDeleteHTMX,
                    LeadSourceListView,
                    ManageLeadSourceHtmx,
                    LeadSourceDeleteHTMX,
                    PotentialListView,
                    ManagePotentialHtmx,
                    PotentialDeleteHTMX,
                    set_language,
                )


app_name = "core"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("configuration", ConfigugrationView.as_view(), name="configuration"),
    path("set_language/<str:language>/", set_language, name="set_language"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    # # tax---------------------------------------------------------------
    path("taxes/", TaxListView.as_view(), name="list_tax"),
    path("taxes/create", ManageTaxHtmx.as_view(), name="create_tax"),
    path("taxes/update/<int:pk>", ManageTaxHtmx.as_view(), name="update_tax"),
    path("taxes/delete/<int:pk>", TaxDeleteHTMX.as_view(), name="delete_tax"),
    path("source_leads/", LeadSourceListView.as_view(), name="list_leadsource"),
    path(
        "source_leads/create/",
        ManageLeadSourceHtmx.as_view(),
        name="create_leadsource",
    ),
    path(
        "source_leads/update/<int:pk>",
        ManageLeadSourceHtmx.as_view(),
        name="update_leadsource",
    ),
    path(
        "source_leads/delete/<int:pk>",
        LeadSourceDeleteHTMX.as_view(),
        name="delete_leadsource",
    ),
    # # Potentiel---------------------------------------------------------------
    path("potentials/", PotentialListView.as_view(), name="list_potential"),
    path("potentials/create", ManagePotentialHtmx.as_view(), name="create_potential"),
    path(
        "potentials/update/<int:pk>",
        ManagePotentialHtmx.as_view(),
        name="update_potential",
    ),
    path(
        "potentials/delete/<int:pk>",
        PotentialDeleteHTMX.as_view(),
        name="delete_potential",
    ),
]
