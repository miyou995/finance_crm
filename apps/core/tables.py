from apps.core.columns import ActionColumn, HTMXUpdateLinkColumn
from apps.core.models import LeadSource, Potential, Tax
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from django.urls import reverse


class TaxHTMxTable(tables.Table):
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )

    name = tables.TemplateColumn(
        template_code="""
        {% if perms.core.change_tax %}
            <a 
                href="#" 
                class="text-gray-800 text-hover-primary fs-5 fw-bold" 
                data-bs-toggle="modal" 
                data-bs-target="#kt_modal" 
                hx-get="{% url 'core:update_tax' record.id %}" 
                hx-target="#kt_modal_content" 
                hx-swap="innerHTML">
                {{ record.name }}
            </a>
        {% else %}
            {{ record.name }}
        {% endif %}
        """,
        verbose_name="Nom",
    )

    tax = tables.Column(verbose_name="Taxe", orderable=True)
    is_active = tables.BooleanColumn(
        verbose_name="Actif", orderable=True, attrs={"td": {"class": "text-end"}}
    )

    class Meta:
        fields = ("counter", "name", "tax", "is_active")
        model = Tax
        template_name = "tables/bootstrap_htmx.html"

    def render_tax(self, value):
        return f"{value}%"

    @property
    def url(self):
        return reverse("core:list_tax")

    @property
    def custom_target(self):
        return "#TaxTable"


class LeadSourceHTMxTable(tables.Table):
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    name = tables.TemplateColumn(
        template_code="""
        {% if perms.core.change_leadsource %}
            <a 
                href="#" 
                class="text-gray-800 text-hover-primary fs-5 fw-bold" 
                data-bs-toggle="modal" 
                data-bs-target="#kt_modal" 
                hx-get="{% url 'core:update_leadsource' record.id %}" 
                hx-target="#kt_modal_content" 
                hx-swap="innerHTML">
                {{ record.name }}
            </a>
        {% else %}
            {{ record.name }}
        {% endif %}
        """,
        verbose_name="Nom",
    )

    class Meta:
        fields = (
            "counter",
            "name",
        )
        model = LeadSource
        template_name = "tables/bootstrap_htmx.html"

    @property
    def url(self):
        return reverse("core:list_leadsource")

    @property
    def custom_target(self):
        return "#SourceTable"


class PotentialHTMxTable(tables.Table):
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    action = ActionColumn()
    segment = HTMXUpdateLinkColumn(accessor="segment", verbose_name=_("Segment"))

    class Meta:
        fields = (
            "counter",
            "segment",
            "min_employees",
            "max_employees",
            "potentiel",
            "action",
        )
        model = Potential
        template_name = "tables/bootstrap_htmx.html"

    @property
    def url(self):
        return reverse("core:list_potential")
