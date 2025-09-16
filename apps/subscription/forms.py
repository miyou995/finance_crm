


from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            "client", "start_date", "end_date", "billing_cycle",
            "next_payment_due", "status", "amount"
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "next_payment_due": forms.DateInput(attrs={"type": "date"}),
        }