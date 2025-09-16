from django import forms
from django.contrib.auth import get_user_model
from apps.billing.models import Invoice
from apps.core.widgets import RichSelect
from apps.crm.models.contact import Contact
from .models import (
    ClientPayment,
    StaffPayment,
    MiscTransaction,
)
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404


User = get_user_model()




class InvoicePaiementModelForm(forms.ModelForm):
    amount = forms.IntegerField(required=False, label="Montant")
    invoice = forms.ModelChoiceField(
        queryset=Invoice.objects.all(),
        widget=RichSelect(
            attrs={
                "class": "form-select form-select-transparent",
                "data-kt-rich-content": "true",
            },
            data_subcontent_field="rest_amount",
        ),
        label=_("Facture"),
    )

    class Meta:
        model = ClientPayment
        fields = ("invoice", "amount", "notes")
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def __init__(self, *args, company_pk=None, invoice_pk=None, **kwargs):
        super().__init__(*args, **kwargs)

        if company_pk:
            self.fields["invoice"].queryset = Invoice.objects.filter(
                lead__company__pk=company_pk
            )

        self._invoice_pk = invoice_pk
        if invoice_pk is not None:
            self.fields.pop("invoice")

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        invoice = self.cleaned_data.get("invoice")
        invoice_pk = getattr(self, "_invoice_pk", None)
        if invoice_pk:
            invoice = get_object_or_404(Invoice, pk=invoice_pk)
        if not amount or amount < 0:
            raise forms.ValidationError(
                _("Montant est requis et doit être supérieur à zéro")
            )
        if amount > invoice.rest_amount:
            raise forms.ValidationError(
                _(
                    "Montant ne peut pas être supérieur au montant restant de la facture."
                )
            )
        return amount

    def save(self, commit=True):
        # 3) Bind the FK on the instance if it was “hidden”
        obj = super().save(commit=False)
        if getattr(self, "_invoice_pk", None):
            obj.invoice_id = self._invoice_pk
        if commit:
            obj.save()
        return obj




class StaffPaymentModelForm(forms.ModelForm):
    staff_member = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label=_("Membre du personnel")
    )
    amount = forms.IntegerField(required=False, label=_("Montant"))

    class Meta:
        model = StaffPayment
        fields = ("staff_member", "amount", "notes")
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if not amount or amount < 0:
            raise forms.ValidationError(
                _("Montant est requis et doit être supérieur à zéro")
            )
        return amount


class IncomeModelForm(forms.ModelForm):
    amount = forms.IntegerField(required=False, label="Montant")
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(), required=False, label="Contact"
    )

    class Meta:
        model = MiscTransaction
        fields = (
            "title",
            "amount",
            "contact",  #
            "notes",
        )
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def __init__(self, *args, contact_pk=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._contact_pk = contact_pk
        if contact_pk is not None:
            self.fields.pop("contact")

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        if not title:
            self.add_error("title", _("Veuillez renseigner ce champ ."))
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if not amount:
            raise forms.ValidationError(_("Veuillez renseigner ce champ"))
        if amount < 0:
            raise forms.ValidationError(_("Montant doit être supérieur à zéro"))
        return amount

    def save(self, commit=True):
        obj = super().save(commit=False)
        if getattr(self, "_contact_pk", None):
            obj.contact_id = self._contact_pk
        if commit:
            obj.save()
        return obj


class ExpenseModelForm(IncomeModelForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.transaction_type = MiscTransaction.TransactionType.EXPENSE
        if commit:
            instance.save()
        return instance


# class ExpenseForm(MiscTransactionForm):
#     def save(self):
#         instance = super().save(commit=False)
#         instance.transaction_type = 'expense'
#         instance.save()
#         return instance
