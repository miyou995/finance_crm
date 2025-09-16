from django import forms
from apps.leads.models import B2BLead, B2CLead


class B2bLeadModelForm(forms.ModelForm):
    class Meta:
        model = B2BLead
        fields = ["title", "company"]

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


class B2cLeadModelForm(forms.ModelForm):
    class Meta:
        model = B2CLead
        fields = ["title", "contact",]

    def __init__(self, *args, contact_pk=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._contact_pk = contact_pk
        if contact_pk is not None:
            self.fields.pop("contact")

    def save(self, commit=True):
        obj = super().save(commit=False)
        if getattr(self, "_contact_pk", None):
            obj.contact_id = self._contact_pk
        if commit:
            obj.save()
        return obj
