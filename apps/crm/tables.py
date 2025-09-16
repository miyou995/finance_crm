import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from apps.core.columns import ActionColumn, CustomCheckBoxColumn, ManyToManyBadgeColumn
from apps.crm.models.company import ActivitySector, Company
from apps.crm.models.contact import Contact
from django.utils import timezone
from django.template.defaultfilters import date
from datetime import timedelta
from django.utils.html import format_html
from apps.core.columns import HTMXLinkColumn


############################# Contact Table ###########################
class ContactHtmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    actions = ActionColumn()
    first_name = tables.Column(
        accessor="first_name", verbose_name=_("Prénom"), orderable=True, linkify=True
    )
    # phones = tables.Column(accessor="phone_numbers", verbose_name=_("Téléphone"), orderable=False)
    phones = tables.ManyToManyColumn(verbose_name=_("Téléphone"))
    emails = tables.ManyToManyColumn(
        verbose_name=_("Email"),
        attrs={"td": {"class": "w-200px p-2 vertical-align-middle"}},
    )
    company = tables.Column(
        accessor="company.name", verbose_name=_("Société"), orderable=True, linkify=lambda record: record.company.get_absolute_url() if record.company else None
    )

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "first_name",
            "last_name",
            "emails",
            "phones",
            "company",
            "actions",
        )
        model = Contact
        template_name = "tables/bootstrap_htmx.html"
        empty_text = _("Aucun contact trouvé.")


########################### Company Table ###########################
class CompanyHtmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    actions = ActionColumn()
    name = tables.Column(
        accessor="name", verbose_name=_("Société"), orderable=True, linkify=True
    )
    tags = ManyToManyBadgeColumn(
        accessor="tags",
        verbose_name=_("Tags"),
        separator=" ",
        orderable=True,
        attrs={"td": {"class": "w-200px p-2 vertical-align-middle"}},
    )
    tax = tables.Column(accessor="annual_tax", verbose_name=_("Taxe"), orderable=True)
    # current_month_revenue = tables.Column(accessor="current_month_revenue", verbose_name=_(f"Réalisation {timezone.now().month}"), orderable=False)
    current_year_revenue = tables.Column(
        accessor="current_year_revenue",
        verbose_name=_(f"Réalisation {timezone.now().year}"),
        orderable=False,
    )
    current_month_revenue = tables.Column(
        accessor="current_month_revenue",
        verbose_name=_(f"Réalisation {date(timezone.now(), 'F')}"),
        orderable=False,
    )
    last_month_revenue = tables.Column(
        accessor="last_month_revenue",
        verbose_name=_(
            f"Réalisation {date(timezone.now().replace(day=1) - timedelta(days=1), 'F')}"
        ),
        orderable=False,
    )

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "name",
            # "business_owner",
            "wilaya",
            "tax",
            "current_year_revenue",
            "current_month_revenue",
            "last_month_revenue",
            "activity_sectors",
            "tags",
            # "employees_count",
            "created_at",
            "actions",
        )

        model = Company
        template_name = "tables/bootstrap_htmx.html"
        empty_text = _("Aucune Entreprise trouvée.")

    def render_current_month_revenue(self, value, record):
        """
        Render the current month revenue with an icon indicating
        increase or decrease compared to last month.
        """

        current_revenue = record.current_month_revenue or 0
        last_revenue = record.last_month_revenue or 0
        # Handle None values
        # if current_revenue is None or last_revenue is None:
        #     return value
        if current_revenue >= last_revenue:
            # Revenue increased or stayed the same
            return format_html(
                '<span class="text-success">{} <i class="fas fa-arrow-up"></i></span>',
                value,
            )
        else:
            # Revenue decreased
            return format_html(
                '<span class="text-danger">{} <i class="fas fa-arrow-down"></i></span>',
                value,
            )


################################ Activity Sector Table ###########################
class ActivitySectorHtmxTable(tables.Table):
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    # name = tables.Column(accessor="name", verbose_name=_("Secteur d'activité"), orderable=True, linkify=True)
    name = HTMXLinkColumn(
        url_name="crm:update_activitysector",
        orderable=True,
        attrs={"th": {"class": "text-start p-3"}},
    )

    class Meta:
        fields = (
            "counter",
            "name",
            "description",
        )
        model = ActivitySector
        template_name = "tables/bootstrap_htmx.html"
