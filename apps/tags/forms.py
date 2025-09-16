from django import forms

from apps.tags.models import Tags


class TagsModelForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ("name",)

    def __init__(self, ticket=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update()

        self.fields["name"].error_messages = {
            "required": "Veuillez renseigner ce champ.",
            "invalid": "Custom error message for field1 is invalid.",
        }
