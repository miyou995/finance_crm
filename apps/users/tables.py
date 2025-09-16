from django.contrib.auth.models import Group
import django_tables2 as tables

from apps.core.columns import (
    ActionColumn,
    CustomCheckBoxColumn,
    ManyToManyBadgeColumn,
)
from .models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class UserHTMxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    email = tables.Column(
        accessor="email", verbose_name=_("Email"), orderable=True, linkify=True
    )
    full_name = tables.Column(
        accessor="full_name",
        verbose_name=_("Nom complet"),
        orderable=True,
        linkify=True,
    )

    tags = ManyToManyBadgeColumn(
        accessor="tags",
        verbose_name=_("Tags"),
        separator=" ",
        orderable=True,
        attrs={"td": {"class": "w-300px p-2 vertical-align-middle"}},
    )
    actions = ActionColumn()

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "full_name",
            "email",
            "tags",
            "is_commercial",
            "is_active",
            "is_staff",
            "actions",
        )
        model = User
        template_name = "tables/bootstrap_htmx.html"


class RoleHTmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    name = tables.TemplateColumn(

        template_code='''
        {% if perms.auth.add_group %}

            <a 
                href="#" 
                class="text-gray-800 text-hover-primary fs-5 fw-bold" 
                data-bs-toggle="modal" 
                data-bs-target="#kt_modal" 
                hx-get="{% url 'users:update_group' record.id %}" 
                hx-target="#kt_modal_content" 
                hx-swap="innerHTML">
                {{ record.name }}
            </a>
        {% else %}
            {{ record.name }}
        {% endif %}
        ''',
        verbose_name=_("Nom"),
    )

    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    actions = ActionColumn()

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "name",
            "actions",
        )
        model = Group
        template_name = "tables/bootstrap_htmx.html"


class UsersPerformanceTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )

    full_name = tables.TemplateColumn(
        """
        <div class="d-flex justify-content-start flex-column">
            <a href="{{record.get_absolute_url}}" class="text-gray-800 fw-bold text-hover-primary mb-1 fs-6">
                {{record.full_name}}
                <span class="text-gray-500 fw-semibold d-block fs-7">{{ record.email }}</span>
            </a>
        </div>
    """,
        verbose_name=_("Nom complet"),
        orderable=True,
        linkify=True,
    )
    # full_name           = tables.Column(orderable=True, linkify=True)
    affected_total = tables.Column(verbose_name=_("Total Affectés"))
    not_treated_total = tables.Column(verbose_name=_("Total Non traité"))
    # completed_total      = tables.Column(verbose_name=_("Total Complétés"))
    # qualified_total     = tables.Column(verbose_name=_("Qualifies en total"))
    affected = tables.Column(verbose_name=_("Affectés"))
    qualified = tables.Column(verbose_name=_("Qualifies"))
    not_qualified = tables.Column(verbose_name=_("Non qualifies"))
    not_interessted = tables.Column(verbose_name=_("Non intéressés"))
    lost = tables.Column(verbose_name=_("Perdus"))
    completed = tables.Column(verbose_name=_("Complétés"))
    injoignable = tables.Column(verbose_name=_("Injoignables"))
    actions = ActionColumn()


class UsersPerformanceB2BTable(UsersPerformanceTable):
    # annual_goal        = tables.Column(verbose_name=_("Objectif annuel"), accessor='annual_goal', orderable=True)
    class Meta:
        fields = (
            "checked_row",
            "counter",
            "full_name",
            # "annual_goal",
            "affected_total",
            "not_treated_total",
            # "completed_total",
            "affected",
            "qualified",
            "not_qualified",
            "not_interessted",
            "injoignable",
            "lost",
            "completed",
            "actions",
        )
        model = User
        template_name = "tables/bootstrap_htmx.html"

    @property
    def url(self):
        return reverse("users:performance_b2b_user")

    @property
    def target(self):
        return "#kt_tab_performance_b2b"


class UsersPerformanceB2CTable(UsersPerformanceTable):
    class Meta:
        fields = (
            "checked_row",
            "counter",
            "full_name",
            # "annual_goal",
            "affected_total",
            "not_treated_total",
            # "completed_total",
            "affected",
            "qualified",
            "not_qualified",
            "not_interessted",
            "injoignable",
            "lost",
            "completed",
            "actions",
        )
        model = User
        template_name = "tables/bootstrap_htmx.html"

    @property
    def url(self):
        return reverse("users:performance_b2c_user")

    @property
    def target(self):
        return "#kt_tab_performance_b2c"
