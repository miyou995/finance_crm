from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


class BooleanAllSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        choices = [("", _("Tout")), ("true", _("Oui")), ("false", _("Non"))]
        super().__init__(
            attrs={
                "class": "form-select filter-select",
                "data-control": "select2",
                "data-hide-search": "true",
            },
            choices=choices,
            *args,
            **kwargs,
        )


class RichSelect(forms.Select):
    """
    A Select widget that adds data-kt-rich-content-* attributes to each <option>
    based on the model instance.
    """

    def __init__(
        self, *args, data_icon_field=None, data_subcontent_field=None, **kwargs
    ):
        self.data_icon_field = data_icon_field
        self.data_subcontent_field = data_subcontent_field
        super().__init__(*args, **kwargs)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option_dict = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs,
        )

        # only proceed if this is a ModelChoiceField
        if hasattr(self.choices, "queryset") and value:
            # try to get the actual model instance
            instance = None

            if hasattr(value, "instance"):
                instance = value.instance
            else:
                # fallback: extract raw PK and re-fetch
                raw_pk = getattr(value, "value", value)
                try:
                    instance = self.choices.queryset.get(pk=raw_pk)
                except Exception:
                    instance = None

            if instance:
                if self.data_subcontent_field:
                    sub = getattr(instance, self.data_subcontent_field, "")
                    option_dict["attrs"]["data-kt-rich-content-subcontent"] = sub
                if self.data_icon_field:
                    icon = getattr(instance, self.data_icon_field, "")
                    option_dict["attrs"]["data-kt-rich-content-icon"] = icon

        return option_dict


class SwitchWidget(forms.CheckboxInput):
    """A custom CheckboxInput widget styled as a toggle switch, using the filter's label dynamically."""

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs.update({"class": "form-check-input"})
        super().__init__(attrs=attrs, *args, **kwargs)
        # Label will be set dynamically in render based on filter context
        self.filter_label = None

    def render(self, name, value, attrs=None, renderer=None):
        """Render the switch widget with the filter's label."""
        # Get the base checkbox HTML
        checkbox_html = super().render(name, value, attrs, renderer)

        # Determine if the checkbox is checked
        is_checked = bool(value) if value is not None else False

        # Use the filter's label if available, fallback to a default
        label_text = self.filter_label or _("Changer")

        # Append " (On)" or " (Off)" to indicate state

        # Render the switch HTML
        return format_html(
            '<label class="form-check form-switch form-check-custom form-check-solid">'
            "{}"
            '<span class="form-check-label fw-semibold text-muted me-2">{}</span>'
            "</label>",
            checkbox_html,
            label_text,
        )


class StatusAllSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(
            attrs={
                "class": "form-select filter-select",
                "data-control": "select2",
                "data-hide-search": "true",
            },
            *args,
            **kwargs,
        )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
