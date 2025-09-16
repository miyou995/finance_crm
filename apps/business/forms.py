from django import forms
from django.forms.models import inlineformset_factory
from apps.business.abstract_models import AbstractLeagal
from apps.business.models import BusinessSettings, BusinessSocials


class InformationForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = (
            "name_company",
            "name_company_arabic",
            "business_owner",
            "business_owner_arabic",
            "wilaya",
            "favicon",
            "logo",
            "logo_negatif",
            "address",
            "email",
            "email2",
            "phone",
            "phone2",
            "phone3",
            "about",
        )


class BusinessAbstractLegalForm(forms.ModelForm):
    class Meta:
        model = AbstractLeagal
        fields = (
            "rc_code",
            "art_code",
            "nif_code",
            "nis_code",
            "bank_number",
            "bank_info",
        )


class BusinessSocialMediaForm(forms.ModelForm):
    class Meta:
        model = BusinessSocials
        fields = (
            "social_type",
            "link",
            "is_active",
            "is_primary",
        )

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("social_type"):
            cleaned_data["skip"] = True
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get("skip", False):
            return None
        # Regular saving logic
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class EmptyBusinessForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = ()


BusinessSocialMediaFormSet = inlineformset_factory(
    BusinessSettings,
    BusinessSocials,
    form=BusinessSocialMediaForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)
