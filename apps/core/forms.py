from django import forms
from apps.core.models import LeadSource, Potential, Tax


class TaxModelForm(forms.ModelForm):

    class Meta:
        fields = ("name", "tax", "is_active")
        model = Tax


class LeadSourceModelForm(forms.ModelForm):

    class Meta:
        fields = ("name",)
        model = LeadSource


class PotentialModelForm(forms.ModelForm):

    class Meta:
        fields = (
            "segment",
            "min_employees",
            "max_employees",
            "potentiel",
        )
        model = Potential
        help_texts = {
            "segment": "Lettre de segmentation (A, B, C..etc)",
            "min_employees": "Nombre minimum d'employés pour ce potentiel",
            "max_employees": "Nombre maximum d'employés pour ce potentiel",
            "potentiel": "Objectif commercial annuel de l'entreprise.",
        }
