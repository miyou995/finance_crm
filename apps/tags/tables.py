from django.urls import reverse
import django_tables2 as tables

from apps.tags.models import Tags


class TagsHTMxTable(tables.Table):
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )

    name = tables.TemplateColumn(
        template_code="""
        {% if perms.tags.change_tags %}
            <a 
                href="#" 
                class="text-gray-800 text-hover-primary fs-5 fw-bold" 
                data-bs-toggle="modal" 
                data-bs-target="#kt_modal" 
                hx-get="{% url 'tags:update_tags' record.id %}" 
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
        model = Tags
        template_name = "tables/bootstrap_htmx.html"

    @property
    def url(self):
        return reverse("tags:list_tags")

    @property
    def custom_target(self):
        return "#TagsTable"
