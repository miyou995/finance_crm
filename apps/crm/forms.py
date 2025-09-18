from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.crm.models.company import (
    ActivitySector,
    Company,
    CompanyDocument,
    CompanyEmail,
    CompanyPhone,
)
from apps.crm.models.contact import Contact, ContactEmail, ContactPhone
from apps.wilayas.models import Commune


##################### Contact Forms #####################
class ContactModelForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "last_name",
            "first_name",
            "civility",
            "company",
            "position",
            "source",
            "address",
            "picture",
            "birth_date",
            "notes",
        )
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def __init__(self, ticket=None, company_pk=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["last_name"].widget.attrs.update()

        self.fields["first_name"].error_messages = {
            "required": "Veuillez renseigner ce champ.",
            "invalid": "Custom error message for field2 is invalid.",
        }
        self.fields["last_name"].error_messages = {
            "required": "Veuillez renseigner ce champ.",
            "invalid": "Custom error message for field1 is invalid.",
        }
        self._company_pk = company_pk
        if company_pk is not None:
            self.fields.pop("company")

    def save(self, commit=True):
        source = self.cleaned_data.get("source")
        obj = super().save(commit=False)
        if getattr(self, "_company_pk", None):
            obj.company_id = self._company_pk
        if commit:
            obj.save()
            if source:
                obj.source.set(source)
        return obj

############ public form URLs ############
class PublicUrlModelForm(ContactModelForm):
    class Meta(ContactModelForm.Meta):
        fields = tuple(f for f in ContactModelForm.Meta.fields if f != "company" and f != "position" and f != "picture")
    
    def save(self, commit=True):
        obj = super().save(commit=False)
        source = self.cleaned_data.get("source")
        if commit:
            obj.save()
            if source:
                obj.source.set(source)
                obj.create_lead()
        return obj



class ContactPhoneModelForm(forms.ModelForm):
    class Meta:
        fields = ("phone",)
        model = ContactPhone

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("phone"):
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


ContactPhoneModelFormSet = inlineformset_factory(
    Contact,
    ContactPhone,
    form=ContactPhoneModelForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)


class ContactEmailModelForm(forms.ModelForm):
    class Meta:
        fields = ("email",)
        model = ContactEmail

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("email"):
            cleaned_data["skip"] = True
        else:
            print("JE SAIS PAS RAHOM NOT VIDE")
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


ContactEmailModelFormSet = inlineformset_factory(
    Contact,
    ContactEmail,
    form=ContactEmailModelForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)


##########################  company forms  ###########################################


class CompanyModelForm(forms.ModelForm):
    lead_name = forms.CharField(
        max_length=100,
        required=False,
        label="Opportunité",
        help_text=_("Entrez le nom de l'opportunité pour cette entreprise, si vide le nom de l'entreprise sera utilisé"),
    )
    create_lead = forms.BooleanField(
        required=False,
        initial=True,
        label="Créer un prospect pour cette entreprise",
        help_text="Cochez cette case pour créer automatiquement un prospect B2C pour cette entreprise",
    )

    class Meta:
        model = Company
        
        fields = (
            "name",
            "business_owner",
            "activity_sectors",
            "tags",
            "employees_count",
            "wilaya",
            "commune",
            "address",
            "website",
            "facebook",
            "notes",
        )
        
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "wilaya" in self.fields:
            self.fields["wilaya"].widget.attrs.update(
                {
                    "class": "form-select",
                    "id": "wilayaId",
                    "hx-get": reverse("wilayas:load_communes"),
                    "hx-swap": "innerHTML",
                    "hx-trigger": "changed, change",
                    "hx-target": "#id_commune",
                }
            )

        # Configure the commune queryset based on wilaya selection
        if "commune" in self.fields:
            self.fields["commune"].queryset = Commune.objects.none()
            self.fields["commune"].widget.attrs.update(
                {
                    "class": "form-select",
                }
            )
            if "wilaya" in self.data:
                wilaya = self.data.get("wilaya")
                if wilaya:
                    self.fields["commune"].queryset = Commune.objects.filter(
                        wilaya=wilaya
                    )
            elif self.instance.pk and "wilaya" in self.fields:
                if self.instance.wilaya:
                    self.fields["commune"].queryset = self.instance.wilaya.commune_set

        if self.instance and self.instance.pk:
            del self.fields["create_lead"]

    def save(self, commit=True):
        company = super().save(commit=False)
        if commit:
            company.set_goal()  
            company.save()
            self.save_m2m()
            if self.cleaned_data.get("create_lead"):
                company.create_lead(lead_name=self.cleaned_data.get("lead_name"))
        return company


class CompanyPhoneModelForm(forms.ModelForm):
    class Meta:
        fields = ("phone",)
        model = CompanyPhone

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("phone"):
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


CompanyPhoneModelFormSet = inlineformset_factory(
    Company,
    CompanyPhone,
    form=CompanyPhoneModelForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)


class CompanyEmailModelForm(forms.ModelForm):
    class Meta:
        fields = ("email",)
        model = CompanyEmail

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("email"):
            cleaned_data["skip"] = True
        else:
            print("JE SAIS PAS RAHOM NOT VIDE")
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


CompanyEmailModelFormSet = inlineformset_factory(
    Company,
    CompanyEmail,
    form=CompanyEmailModelForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)


class CompanyFinancialModelForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "capital",
            "bank_name",
            "nif",
            "nrc",
            "nart",
            "nis",
        )


class CompanyDocumentModelForm(forms.ModelForm):
    class Meta:
        model = CompanyDocument
        fields = (
            "company",
            "document",
            "description",
        )

    def __init__(self, *args, company_pk=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._company_pk = company_pk
        if company_pk is not None:
            self.fields.pop("company")

    def save(self, commit=True):
        obj = super().save(commit=False)
        if getattr(self, "_company_pk", None):
            obj.company_id = self._company_pk
        if commit:
            obj.save()
        return obj


############################# secteur d'activité forms #############################


class ActivitySectorModelForm(forms.ModelForm):
    class Meta:
        model = ActivitySector
        fields = ("name", "description")
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Description du secteur..."}
            ),
        }
