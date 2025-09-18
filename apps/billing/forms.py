from apps.billing.models import Bill, Invoice, Quote, BillLine
from django import forms
from django.forms.models import inlineformset_factory
from apps.core.widgets import RichSelect
from apps.leads.models import B2BLead


# ############################# Invoice Forms #############################


# class InvoiceModelForm(forms.ModelForm):
#     lead = forms.ModelChoiceField(
#         queryset=B2BLead.objects.all(),  # we’ll set it in __init__
#         widget=RichSelect(
#             attrs={
#                 "class": "form-select form-select-transparent",
#                 "data-kt-rich-content": "true",
#             },
#             data_subcontent_field="company",  # your B2BLead field for the subtitle
#         ),
#         label="Opportunité",
#     )

#     class Meta:
#         model = Invoice
#         fields = (
#             "lead",
#             "creation_date",
#             "due_date",
#         )

#         widgets = {
#             "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
#             "creation_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
#         }

#     def __init__(self, *args, company_pk=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         if company_pk:
#             try:
#                 self.fields["lead"].queryset = B2BLead.objects.filter(
#                     company__pk=company_pk
#                 )
#             except B2BLead.DoesNotExist:
#                 pass


# class InvoiceItemForm(forms.ModelForm):
#     class Meta:
#         model = BillLine
#         fields = (
#             "title",
#             "description",
#             "quantity",
#             "unit_price",
#             "unit",
#             "discount",
#         )
#         widgets = {
#             "description": forms.Textarea(attrs={"rows": 2,"class": "w-250px"}),
#             "title": forms.TextInput(attrs={"class": "w-200px"}),
#             "quantity": forms.NumberInput(attrs={"class": "w-70px"}),
#             "unit_price": forms.NumberInput(attrs={"class": "w-100px"}),
#             "unit": forms.TextInput(attrs={"class": "w-70px"}),
#             "discount": forms.NumberInput(attrs={"class": "w-100px"}),
#         }
        
#     def clean(self):
#         cleaned_data = super().clean()
#         quantity = cleaned_data.get("title")
#         if not quantity:
#             cleaned_data["skip"] = True
#         return cleaned_data

#     def save(self, commit=True):
#         if self.cleaned_data.get("skip", False):
#             return None
#         instance = super().save(commit=False)
#         if commit:
#             instance.save()
#             self.save_m2m()
#         return instance


# InvoiceItemModelFormSet = inlineformset_factory(
#     Invoice,
#     BillLine,
#     form=InvoiceItemForm,
    
#     extra=0,
#     min_num=1,
#     can_delete=True,
#     can_delete_extra=True,
# )



############################# Quote Forms #############################



class BillModelForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=Bill.BillStates.choices,  # noqa: F821
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    lead = forms.ModelChoiceField(
        queryset=B2BLead.objects.none(),  # we’ll set it in __init__
        widget=RichSelect(
            attrs={
                "class": "form-select form-select-transparent",
                "data-kt-rich-content": "true",
            },
            data_subcontent_field="company",  # your B2BLead field for the subtitle
        ),
        label="Opportunité",
    )

    class Meta:
        model = Quote
        fields = (
            "lead",
            "creation_date",
            "due_date",
            "bill_total",
            "bill_discount",
            "notes",
        )

        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "creation_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, company_pk=None, lead_pk=None, **kwargs):
        super().__init__(*args, **kwargs)
        print('\n \n \n \n self.instance:', self.instance)
        if company_pk:
            self.fields["lead"].queryset = B2BLead.objects.filter(
                company__pk=company_pk
            ).select_related("company")
        else:
            self.fields["lead"].queryset = B2BLead.objects.select_related("company")
            
        self._lead_pk = lead_pk
        print('self._lead_pk:', self._lead_pk)
        if lead_pk is not None:
            self.fields.pop("lead")
            
    def save(self, commit=True):
        source = self.cleaned_data.get("source")
        obj = super().save(commit=False)
        if getattr(self, "_lead_pk", None):
            obj.lead_id = self._lead_pk
        if commit:
            obj.save()
            if source:
                obj.source.set(source)
        return obj
   
class InvoiceModelForm(BillModelForm):
    class Meta(BillModelForm.Meta):
        model = Invoice
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.bill_type = Bill.BillTypes.INVOICE
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class QuoteModelForm(BillModelForm):
    class Meta(BillModelForm.Meta):
        model = Quote
        
    def save(self, commit=True):

        instance = super().save(commit=False)
        instance.bill_type = Bill.BillTypes.QUOTE
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class BillLineForm(forms.ModelForm):
    class Meta:
        model = BillLine
        fields = (
            "title",
            "description",
            "quantity",
            "unit_price",
            "unit",
            "discount",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2,"class": "w-250px"}),
            "title": forms.TextInput(attrs={"class": "w-200px"}),
            "quantity": forms.NumberInput(attrs={"class": "w-70px"}),
            "unit_price": forms.NumberInput(attrs={"class": "w-100px"}),
            "unit": forms.TextInput(attrs={"class": "w-70px"}),
            "discount": forms.NumberInput(attrs={"class": "w-100px"}),
        }
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get("title")
        if not quantity:
            cleaned_data["skip"] = True
        return cleaned_data




InvoiceItemModelFormSet = inlineformset_factory(
    Invoice,
    BillLine,
    form=BillLineForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)

QuoteItemModelFormSet = inlineformset_factory(
    Quote,
    BillLine,
    form=BillLineForm,
    extra=0,
    min_num=1,
    can_delete=True,
    can_delete_extra=True,
)
