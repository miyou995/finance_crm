from django import forms
from django.contrib.auth import get_user_model
from apps.billing.models import Quote, Invoice,  Bill
from apps.core.widgets import RichSelect
from apps.crm.models import Contact, Company
from .models import (
    ClientPayment,
    StaffPayment,
    MiscTransaction,
)
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404


User = get_user_model()




class BillPaiementModelForm(forms.ModelForm):
    amount = forms.IntegerField(required=False, label="Montant")
    bill = forms.ModelChoiceField(
        queryset=Bill.objects.unpaid(),
        widget=RichSelect(
            attrs={
                "class": "form-select form-select-transparent",
                "data-kt-rich-content": "true",
            },
            data_subcontent_field="get_company_and_rest",
        ),
        label=_("Facture"),
        required=False,
    )

    class Meta:
        model = ClientPayment
        fields = ("bill", "amount", "notes")
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Notes supplémentaires..."}
            ),
        }

    def __init__(self, *args, company_pk=None, bill_pk=None, bill_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_pk = company_pk
        self.bill_type = bill_type
        print('bill_type>>>', bill_type)
        if company_pk:
            self.fields["bill"].queryset = self.fields["bill"].queryset.filter(
                lead__company__pk=company_pk
            )
            
        self.fields["bill"].queryset.count()
        if bill_type:
            self.fields["bill"].queryset = self.fields["bill"].queryset.filter(
                bill_type=bill_type
            )
            self.fields["bill"].queryset.count()
            

        self._bill_pk = bill_pk
        if bill_pk is not None:
            self.fields.pop("bill")

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        bill = self.cleaned_data.get("bill")
        bill_pk = getattr(self, "_bill_pk", None)
        if bill_pk:
            bill = get_object_or_404(Bill, pk=bill_pk)
            if not amount or amount < 0:
                raise forms.ValidationError(
                    _("Montant est requis et doit être supérieur à zéro")
                )
            if amount > bill.rest_amount:
                raise forms.ValidationError(
                    _(
                        "Montant ne peut pas être supérieur au montant restant de la facture."
                    )
                )
        return amount

    def save(self, commit=True):
        # 3) Bind the FK on the instance if it was “hidden”
        obj = super().save(commit=False)
        
        print('self._bill_pk>>>', self._bill_pk)
        if getattr(self, "_bill_pk", None):
            obj.bill_id = self._bill_pk
            obj.client = Bill.objects.filter(pk=self._bill_pk).first().lead.company
        elif self.company_pk:
            obj.client = get_object_or_404(Company, pk=self.company_pk)
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
