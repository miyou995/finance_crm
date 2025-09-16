import django_tables2 as tables
from django.utils.translation import gettext as _
from apps.core.columns import ActionColumn, BadgeColumn, CustomCheckBoxColumn
from apps.leads.models import B2BLead, B2BLeadState, B2CLead


class B2bHtmxLeadTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )
    title = tables.Column(
        verbose_name="Titre", accessor="title", orderable=True, linkify=True
    )
    company = tables.Column(
        verbose_name="Entreprise", accessor="company.name", orderable=True
    )
    agent = tables.Column(
        verbose_name="Agent", accessor="current_state_user", orderable=True
    )
    current_state = BadgeColumn(
        color_field="get_status_color", label_field="get_current_state"
    )

    actions = ActionColumn()

    class Meta:
        model = B2BLead
        template_name = "tables/bootstrap_htmx.html"
        fields = (
            "checked_row",
            "counter",
            "title",
            "company",
            "agent",
            "current_state",
            "created_at",
            "actions",
        )
        empty_text = _("Aucune Opportuniée trouvée.")

    def __init__(self, *args, company_pk=None, **kwargs):
        self.company_pk = company_pk
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if self.company_pk is not None:
            self.columns.hide("company")

    # @property
    # def url(self):
    #     return reverse('leads:all_b2b_lead_list')


class B2cHtmxLeadTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )
    title = tables.Column(
        verbose_name="Titre", accessor="title", orderable=True, linkify=True
    )
    first_name = tables.Column(
        verbose_name="Prénom", accessor="contact.first_name", orderable=True
    )
    last_name = tables.Column(
        verbose_name="Nom", accessor="contact.last_name", orderable=True
    )
    company = tables.Column(
        verbose_name="Entreprise", accessor="contact.company", orderable=True
    )
    agent = tables.Column(
        verbose_name="Agent", accessor="current_state_user", orderable=True
    )
    current_state = BadgeColumn(
        color_field="get_status_color", label_field="get_current_state"
    )

    actions = ActionColumn()

    def __init__(self, pk=None, *args, **kwargs):
        self.pk = pk
        super().__init__(*args, **kwargs)

    class Meta:
        model = B2CLead
        template_name = "tables/bootstrap_htmx.html"

        fields = (
            "checked_row",
            "counter",
            "title",
            "first_name",
            "last_name",
            "company",
            "agent",
            "current_state",
            "created_at",
            "actions",
        )
        empty_text = _("Aucune Opportuniée trouvée.")

    def before_render(self, request):
        if self.pk is not None:
            self.columns.hide("checked_row")
            self.columns.hide("first_name")
            self.columns.hide("last_name")


class LeadStateTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )
    lead = tables.Column(verbose_name="Lead", accessor="lead", orderable=True)
    notes = tables.Column(verbose_name="Notes", accessor="notes", orderable=True)
    # lead = tables.Column(verbose_name="Entreprise", accessor='company.name', orderable=True)
    # created_by  = tables.Column(verbose_name="Agent", accessor='created_by', orderable=True)
    state = BadgeColumn("get_state_color", "get_current_state")
    # current_state   = BadgeColumn("lead__get_state_color", "lead__get_current_state")
    created_at = tables.Column(
        verbose_name="Date de création", accessor="created_at", orderable=True
    )

    class Meta:
        template_name = "tables/bootstrap_htmx.html"
        fields = (
            "checked_row",
            "counter",
            # 'title',
            "lead",
            "notes",
            "created_by",
            "state",
            "created_at",
            # 'current_state',
        )
        empty_text = _("Aucune Action réalisée.")


class B2BLeadStateTable(LeadStateTable):
    class Meta(LeadStateTable.Meta):
        model = B2BLeadState
