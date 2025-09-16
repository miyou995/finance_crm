from django import forms
from apps.leads.models import B2BLead, B2CLead
from apps.appointment.models import Appointment


class AppointmentLeadB2bForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["state", "date", "subject", "notes", "report"]

        widgets = {
            "date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        self.lead_b2b_pk = kwargs.pop("lead_b2b_pk", None)
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.lead_b2b_pk and not instance.pk:
            try:
                lead = B2BLead.objects.get(pk=self.lead_b2b_pk)
                instance.b2b_lead = lead
            except B2BLead.DoesNotExist:
                lead = None

        if commit:
            instance.save()
            if hasattr(self, "request") and self.request:
                print(f"---------->>>>>>Setting user {self.request.user} for appointment")
                instance.users.set([self.request.user])
            self.save_m2m()
        return instance


class AppointmentLeadB2cForm(AppointmentLeadB2bForm):

    def __init__(self, *args, **kwargs):
        self.lead_b2c_pk = kwargs.pop("lead_b2c_pk", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.lead_b2c_pk and not instance.pk:
            try:
                lead = B2CLead.objects.get(pk=self.lead_b2c_pk)
                instance.b2c_lead = lead
            except B2CLead.DoesNotExist:
                lead = None

        if commit:
            instance.save()
            if hasattr(self, "request") and self.request:
                instance.users.set([self.request.user])
            self.save_m2m()
        return instance
