# from django import forms
# from apps.leads.models import Lead
# from apps.notification.models import Notification
# from django.utils.translation import gettext_lazy as _


# class NotificationForm(forms.ModelForm):
#     state = forms.ChoiceField(
#         choices=[
#             (Notification.States.APPOINTMENT, _("Rendez-vous")),
#             (Notification.States.RECALL, _("Rappel")),
#         ],
#     )


#     class Meta:
#         model = Notification
#         fields = ['state', 'date', 'message',]

#         widgets = {
#             'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         }
#     def __init__(self, *args, **kwargs):
#         self.lead_pk = kwargs.pop('lead_pk', None)
#         super().__init__(*args, **kwargs)

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if self.lead_pk:
#             try:
#                 lead = Lead.objects.get(pk=self.lead_pk)
#                 instance.content_object = lead
#             except Lead.DoesNotExist:
#                 lead = None
#         if commit:
#             instance.save()
#         return instance
