import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, conditional_escape
from django.urls import reverse
from django_tables2.utils import computed_values, Accessor
from django.utils.safestring import mark_safe


class IsActiveColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        template = """
            {% if record.is_active %}
                <div class="badge badge-light-success">{% translate "Active" %}</div>
            {% else %}
                <div class="badge badge-light-danger">{% translate "Not Active" %}</div>
            {% endif %}
        """
        super(IsActiveColumn, self).__init__(
            template, verbose_name=_("Active"), orderable=False, *args, **kwargs
        )


class HTMXLinkColumn(tables.Column):
    def __init__(self, url_name, *args, **kwargs):
        super(HTMXLinkColumn, self).__init__(*args, **kwargs)
        self.url_name = url_name

    def render(self, value, record):
        if value:
            href = reverse(self.url_name, args=[record.pk])
            return format_html(
                '<a href="#" class="text-gray-800 text-hover-primary fs-5 fw-bold" '
                'data-bs-toggle="modal" data-bs-target="#kt_modal" '
                'hx-get="{}" hx-target="#kt_modal_content" hx-swap="innerHTML">{}</a>',
                href,
                value,
            )
        else:
            return "-"

    #  def render(self, value, record):
    # model = record.__class__._meta
    # print('self.CLASSSS', model)
    # print('self.app_label', model.app_label)
    # print('self.model_name', model.model_name)
    # permission = f"perms.{model.app_label}.view_{model.model_name}"
    # if value:
    #     href = reverse(self.url_name, args=[record.pk])
    #     return format_html(
    #         '<a href="#" class="text-gray-800 text-hover-primary fs-5 fw-bold" '
    #         'data-bs-toggle="modal" data-bs-target="#kt_modal" '
    #         '{% if perms.foo.view_vote %}'
    #         'hx-get="{}" hx-target="#kt_modal_content" hx-swap="innerHTML">{}</a>'
    #         '{% endif %}',
    #         permission, href, value
    #     )
    # else:
    #     return '-'


class HTMXUpdateLinkColumn(tables.Column):
    """
    Renders a link that opens a modal and loads the object's get_update_url.
    Assumes the record has a get_update_url() method.
    """

    def render(self, value, record):
        try:
            href = record.get_update_url()
        except Exception as e:
            print("Error getting update URL:", e)
            href = "#"
        if value:
            return format_html(
                '<a href="#" class="text-gray-800 text-hover-primary fs-5 fw-bold" '
                'data-bs-toggle="modal" data-bs-target="#kt_modal" '
                'hx-get="{}" hx-target="#kt_modal_content" hx-swap="innerHTML">{}</a>',
                href,
                value,
            )
        else:
            return "-"


class HTMXDeleteLinkColumn(tables.Column):
    def __init__(self, url_name=None, *args, **kwargs):
        super(HTMXDeleteLinkColumn, self).__init__(*args, **kwargs)
        self.url_name = url_name

    def render(self, value, record):
        if value:
            try:
                href = reverse(self.url_name, args=[record.pk])
            except Exception as e:
                print("Error in reverse URL for delete:", e)
                href = "#"
            return format_html(
                '<a href="#" class="text-gray-800 text-hover-primary fs-5 fw-bold" '
                'data-bs-toggle="modal" data-bs-target="#delete_modal" '
                'hx-get="{}" hx-target="#delete_modal_body" hx-swap="innerHTML">{}</a>',
                href,
                value,
            )
        else:
            return "-"


class HTMXCircleColumn(tables.Column):
    def __init__(self, url_name, *args, **kwargs):
        super(HTMXCircleColumn, self).__init__(*args, **kwargs)
        self.url_name = url_name

    def render(self, value, record):
        if value:
            href = reverse(self.url_name, args=[record.pk])
            # print('THE IMAGE name',record.name)
            return format_html(
                """
                    <div class="symbol symbol-circle symbol-50px overflow-hidden me-3 cursor-pointer">
                        <a 
                            data-bs-toggle="modal" 
                            data-bs-target="#kt_modal" 
                            hx-get="{}" 
                            hx-target="#kt_modal_content" 
                            hx-swap="innerHTML"
                        >
                            <div class="symbol-label fs-3 bg-light-danger text-danger text-uppercase">{}</div>
                        </a>
                    </div>
                """,
                href,
                record.get_extension,
            )
        else:
            return "-"


class CustomCheckBoxColumn(tables.CheckBoxColumn):
    def __init__(self, *args, **kwargs):
        if "attrs" not in kwargs:
            kwargs["attrs"] = {
                "th__input": {
                    "class": "form-check-input border-dark ",
                    "id": "select_all",
                    "data-kt-check": "true",
                    "data-kt-check-target": ".checked-cel .form-check-input",
                },
                "td": {
                    "class": "checked-cel w-50px",
                },
            }
        super().__init__(*args, **kwargs)

    def render(self, value, bound_column, record):
        default = {"type": "checkbox", "name": bound_column.name, "value": value}
        if self.is_checked(value, record):
            default.update({"checked": "checked"})
        general = self.attrs.get("input")
        specific = self.attrs.get("td__input")
        attrs = dict(default, **(specific or general or {}))
        attrs = computed_values(attrs, kwargs={"record": record, "value": value})
        # {AttributeDict(attrs).as_html()}
        return mark_safe(
            f"""
                    <div class="form-check form-check-custom p-3">
                        <input
                            class="form-check-input border-dark"
                            form="actionsForm"
                            name="selected_rows"
                            type="checkbox"
                            value="{record.pk}"
                            
                        />
                    </div>
                """
        )



class BadgeColumn(tables.Column):
    """
    Usage: BadgeColumn('color_field', 'label_field')
    Renders a badge with the color from the first field and the label from the second.
    """

    def __init__(self, color_field, label_field, *args, **kwargs):
        self.color_accessor = Accessor(color_field)
        self.label_accessor = Accessor(label_field)
        super().__init__(*args, **kwargs)

    def render(self, value, record):
        color = self.color_accessor.resolve(record) or "secondary"
        label = self.label_accessor.resolve(record) or value or ""
        return mark_safe(
            f'<span class="badge badge-outline badge-{color}">{label}</span>'
        )


class ActionColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        template = """{% include 'buttons/action.html' with object=record modal_edit="true" %}"""
        attrs = {"td": {"class": "text-end"}}  # this doesn't work

        super(ActionColumn, self).__init__(
            template,
            verbose_name=_("Actions"),
            orderable=False,
            attrs=attrs,
            *args,
            **kwargs,
        )


class ManyToManyBadgeColumn(tables.ManyToManyColumn):
    def render(self, value):
        items = []
        for item in self.filter(value):
            content = conditional_escape(self.transform(item))
            if hasattr(self, "linkify_item"):
                content = self.linkify_item(content=content, record=item)
            # Wrap each item in the badge HTML
            badge_content = f'<div class="badge badge-light-secondary">{content}</div>'
            items.append(badge_content)

        return mark_safe(conditional_escape(self.separator).join(items))


class PrintColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        template = """
					<a class="btn btn-primary btn-sm" href="{% url 'transactions:impression_resu_paiement' paiement_id=record.pk %}" 
						target="_blank">A4/2</a>
		"""
        super(PrintColumn, self).__init__(
            template, verbose_name=_("Impression"), orderable=False, *args, **kwargs
        )


class PrintTransactionColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        template = """
				<a class="btn btn-primary btn-sm" href="{% url 'transactions:impression_resu_autre_transaction' transaction_id=record.pk %}" 
						target="_blank">A5/2</a>
				
			
		"""
        super(PrintTransactionColumn, self).__init__(
            template, verbose_name=_("Impression"), orderable=False, *args, **kwargs
        )


class AbonnementValidColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        template = """
            {% if record.is_valid %}
                <div class="badge badge-light-success">{% translate "Valide" %}</div>
            {% else %}
                <div class="badge badge-light-danger">{% translate "Non Valide" %}</div>
            {% endif %}
        """
        super(AbonnementValidColumn, self).__init__(
            template, verbose_name=_("valide"), orderable=False, *args, **kwargs
        )
