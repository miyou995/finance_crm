import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from apps.core.columns import (
    ActionColumn,
    BadgeColumn,
    CustomCheckBoxColumn,
    PrintColumn,
    PrintTransactionColumn,
)
from .models import (
    ClientPayment,
    LedgerEntry,
    StaffPayment,
    MiscTransaction,
)


class TransactionBaseTable(tables.Table):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )

    impression = PrintColumn()
    user = tables.Column(
        accessor="created_by", verbose_name=_("Créé par"), orderable=True, linkify=True
    )
    action = ActionColumn()


class ClientPaymentHTMxTable(TransactionBaseTable):
    checked_row = CustomCheckBoxColumn(accessor="pk", orderable=False)
    counter = tables.TemplateColumn(
        verbose_name="N°",
        template_code="{{ row_counter|add:'1' }}",
        orderable=False,
    )
    bill = tables.Column(
        accessor="bill", verbose_name=_("document"), orderable=True, linkify=True
    )
    company = tables.Column(
        accessor="bill__lead__company",
        verbose_name=_("Société"),
        orderable=True,
        linkify=True,
    )
    amount = tables.Column(
        accessor="amount", verbose_name=_("Montant Payé"), orderable=True
    )
    doc_type = tables.Column(
        accessor="bill__bill_type", verbose_name=_("Document"), orderable=True
    )
    # rest_amount = tables.Column(accessor="rest_amount", verbose_name=_("Montant restant"), orderable=True)
    rest_amount = tables.TemplateColumn(
        verbose_name=_("Montant restant"),
        template_code="""
 				{% if record.bill.rest_amount == 0 %}
                	<span style="color: green;">payé</span>
                {% else %}
                	<span style="color: red;">{{ record.bill.rest_amount }}</span>
                {% endif %}""",
    )

    class Meta:
        exclude = ("impression",)
        fields = (
            "checked_row",
            "counter",
            "bill",
            "company",
            "amount",
            "rest_amount",
            "user",
            "notes",
            "date",
        )
        model = ClientPayment
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
            return reverse(
                "transactions:company_invoices_payment", kwargs={"pk": self.company_pk}
            )
        return reverse("transactions:list_clientpayment")


class AutreTransactionTableHTMxTable(TransactionBaseTable):
    transaction_type = BadgeColumn(
        "get_transaction_color",
        "transaction_type",
        verbose_name=_("Type de transaction"),
    )
    user = tables.Column(
        accessor="created_by", verbose_name=_("Créé par"), orderable=True, linkify=False
    )
    impression = PrintTransactionColumn()
    action = ActionColumn()

    def __init__(self, contact=None, *args, **kwargs):
        self.contact = contact
        super().__init__(*args, **kwargs)

    class Meta:
        fields = (
            "checked_row",
            "counter",
            "title",
            "user",
            "amount",
            "contact",
            "transaction_type",
            "notes",
            "date",
            "impression",
            "action",
        )
        model = MiscTransaction

    @property
    def url(self):
        return reverse("transactions:list_misctransaction")

    def before_render(self, request):
        if self.contact is not None:
            self.columns.hide("checked_row")
            self.columns.hide("contact")
            
            
class LedgerEntryTable(TransactionBaseTable):
    entry_type = BadgeColumn(
        "get_transaction_color", "entry_type", verbose_name=_("Type de transaction")
    )
    transaction = tables.Column(
        accessor="get_transaction_type", verbose_name=_("Nature"), orderable=True
    )
    suppression = tables.TemplateColumn(
        verbose_name=_("Action"),
        orderable=False,
        template_code="""
        {% if not record.client_payment and not record.staff_payment and not record.misc_transaction %}
            <a 
                class="btn btn-sm btn-danger"
                hx-get="{% url 'transactions:delete_ledgerentry' record.pk %}"
                hx-target="#delete_modal_body"
                hx-swap="innerHTML"
                data-bs-toggle="modal"
                data-bs-target="#delete_modal"
            >
                <i class="fa fa-trash"></i>
            ++++++63.
            </a>
        {% else %}
            <button 
                type="button"
                class="btn btn-sm btn-danger"
                disabled
                aria-disabled="true"
            >
                <i class="fa fa-trash"></i>
            </button>
        {% endif %}
        """,
    )

    def __init__(self, contact=None, *args, **kwargs):
        self.contact = contact
        super().__init__(*args, **kwargs)

    class Meta:
        exclude = ("impression", "user")
        fields = (
            # "checked_row",
            "counter",
            "user",
            "description",
            "created_by",
            "amount",
            "transaction",
            "entry_type",
            "date",
            "suppression",
        )
        model = LedgerEntry
    def before_render(self, request):
        self.columns.hide("action")
        self.columns.hide("checked_row")

    @property
    def url(self):
        return reverse("transactions:ledger_entry")


class StaffPaymentHTMxTable(TransactionBaseTable):
    staff_member = tables.Column(
        accessor="staff_member.full_name",
        verbose_name=_("Membre du personnel"),
        orderable=True,
        linkify=False,
    )

    class Meta:
        exclude = ("impression",)
        fields = (
            "checked_row",
            "counter",
            "staff_member",
            "amount",
            "date",
            "user",
            "notes",
        )
        model = StaffPayment

    @property
    def url(self):
        return reverse("transactions:list_staffpayment")

