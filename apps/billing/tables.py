import django_tables2 as tables
from django.urls import reverse
from apps.billing.models import Invoice, Quote
from apps.core.columns import ActionColumn, BadgeColumn, CustomCheckBoxColumn
from django.utils.translation import gettext_lazy as _


############################# Invoice Tables #############################


class InvoiceHtmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    bill_number = tables.Column(
        accessor="bill_number", verbose_name="Facture N°", orderable=True, linkify=True
    )
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    actions = ActionColumn()

    company = tables.Column(accessor="lead.company.name", verbose_name="Société", orderable=True)
    state = BadgeColumn("get_state_color", "get_state_display")  
    due_date = tables.Column(accessor="get_due_date_with_number_of_days", verbose_name="Date d'échéance", orderable=True)
    total_amount = tables.Column(accessor="get_total_ttc", verbose_name="Montant TTC", orderable=True)
    rest_amount = tables.Column(accessor="rest_amount", verbose_name="Montant restant", orderable=True)

    # rest_amount = tables.TemplateColumn(
    # 	template_code='''
    # 			{% if record.rest_amount == 0 %}
    #             	<span style="color: green;">payé</span>
    #             {% else %}
    #             	<span style="color: red;">{{ record.rest_amount }}</span>
    #             {% endif %}'''
    # )
    class Meta:
        fields = (
            "checked_row",
            "counter",
            "bill_number",
            "company",
            "total_amount",
            "rest_amount",
            "state",
            "due_date",
            "created_at",
        )

        model = Invoice
        template_name = "tables/bootstrap_htmx.html"
        empty_text = _("Aucune Facture trouvée.")

    def __init__(self, *args, company_pk=None, **kwargs):
        self.company_pk = company_pk
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if self.company_pk is not None:
            self.columns.hide("company")

    @property
    def url(self):
        if self.company_pk:
            return reverse("billing:company_invoices", kwargs={"pk": self.company_pk})
        return reverse("billing:list_invoice")


#################################### Quote Tables ####################################
class QuoteHtmxTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        "{{ row_counter|add:1 }}", orderable=False, verbose_name="N°"
    )
    bill_number = tables.Column(
        accessor="bill_number", verbose_name="Devis N°", orderable=True, linkify=True
    )
    actions = ActionColumn()

    company = tables.Column(accessor="lead.company.name", verbose_name="Société", orderable=True)
    state = BadgeColumn("get_state_color", "get_state_display")  
    due_date = tables.Column(accessor="get_due_date_with_number_of_days", verbose_name="Date d'échéance", orderable=True)
    total_amount = tables.Column(accessor="get_total_ttc", verbose_name="Montant TTC", orderable=True)
    

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "bill_number",
            "company",
            "total_amount",
            "state",
            "due_date",
            "created_at",
        )

        model = Quote
        template_name = "tables/bootstrap_htmx.html"

    def __init__(self, *args, company_pk=None, **kwargs):
        self.company_pk = company_pk
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if self.company_pk is not None:
            self.columns.hide("company")

    @property
    def url(self):
        if self.company_pk:
            return reverse("billing:company_quotes", kwargs={"pk": self.company_pk})
        return reverse("billing:list_quote")
