from django.views.generic import ListView
from apps.business.forms import (
    BusinessAbstractLegalForm,
    BusinessSocialMediaFormSet,
    EmptyBusinessForm,
    InformationForm,
)
from apps.business.models import BusinessSettings, BusinessSocials
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from apps.core.mixins import BaseManageHtmxFormView, BreadcrumbMixin, DeleteMixinHTMX


###################### Business Settings Management ####################


class BusinessSettingsView(BreadcrumbMixin, PermissionRequiredMixin, ListView):
    permission_required = "business.view_businesssettings"
    model = BusinessSettings
    template_name = "business_settings.html"
    context_object_name = "business_settings"


class ManageBusinessInformation(BaseManageHtmxFormView):
    permission_required = "business.add_businesssettings"
    form_class = InformationForm
    model = BusinessSettings

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = BusinessSettings.objects.first()
        if not instance:
            instance = BusinessSettings.objects.create()
        kwargs["instance"] = instance
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse("business:create_businesssettings")
        context["update_url"] = reverse(
            "business:update_businesssettings", kwargs={"pk": self.get_object().pk}
        )
        return context


class DeleteBusinessSettings(DeleteMixinHTMX):

    model = BusinessSettings


# ############## Social Media Management ####################


class ManageBusinessSocialMediaHTMX(BaseManageHtmxFormView):
    form_class = EmptyBusinessForm
    model = BusinessSettings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse("business:create_social_media")
        context["update_url"] = reverse(
            "business:update_social_media", kwargs={"pk": self.get_object().pk}
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = BusinessSettings.objects.first()
        if not instance:
            instance = BusinessSettings.objects.create()
        kwargs["instance"] = instance
        return kwargs

    def get_formsets(self):
        instance = self.get_object()
        return {
            "social_media": BusinessSocialMediaFormSet(
                self.request.POST or None, instance=instance, prefix="social_media"
            ),
        }


class DeleteBusinessSocials(DeleteMixinHTMX):
    model = BusinessSocials


class BusinessAbstractLegal(BaseManageHtmxFormView):
    permission_required = "business.add_businesssettings"
    form_class = BusinessAbstractLegalForm
    model = BusinessSettings

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = BusinessSettings.objects.first()
        if not instance:
            instance = BusinessSettings.objects.create()
        kwargs["instance"] = instance
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse("business:create_abstractlegal")
        context["update_url"] = reverse(
            "business:update_abstractlegal", kwargs={"pk": self.get_object().pk}
        )
        return context
