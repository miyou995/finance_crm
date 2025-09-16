from django.urls import path
from apps.business.views import (
                                BusinessSettingsView,
                                ManageBusinessInformation,
                                DeleteBusinessSettings,
                                ManageBusinessSocialMediaHTMX,
                                DeleteBusinessSocials,
                                BusinessAbstractLegal
                            )


app_name = "business"


urlpatterns = [
    path("settings/", BusinessSettingsView.as_view(), name="business_settings"),
    ######### Business Settings Management #########
    path(
        "settings/information/",
        ManageBusinessInformation.as_view(),
        name="create_businesssettings",
    ),
    path(
        "settings/information/update/<int:pk>/",
        ManageBusinessInformation.as_view(),
        name="update_businesssettings",
    ),
    path(
        "settings/information/delete/<int:pk>/",
        DeleteBusinessSettings.as_view(),
        name="delete_businesssettings",
    ),
    ######### Social Media Management #########
    path(
        "settings/social_media/",
        ManageBusinessSocialMediaHTMX.as_view(),
        name="create_social_media",
    ),
    path(
        "settings/social_media/update/<int:pk>/",
        ManageBusinessSocialMediaHTMX.as_view(),
        name="update_social_media",
    ),
    path(
        "settings/social_media/delete/<int:pk>/",
        DeleteBusinessSocials.as_view(),
        name="delete_social_media",
    ),
    ######### Business Abstract Legal Management #########
    path(
        "settings/abstract_legal/",
        BusinessAbstractLegal.as_view(),
        name="create_abstractlegal",
    ),
    path(
        "settings/abstract_legal/update/<int:pk>/",
        BusinessAbstractLegal.as_view(),
        name="update_abstractlegal",
    ),
    path(
        "settings/abstract_legal/delete/<int:pk>/",
        BusinessAbstractLegal.as_view(),
        name="delete_abstractlegal",
    ),
]
