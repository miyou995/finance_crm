from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import CRUDUrlMixin, Tax, TimestampedModel
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Q

User = get_user_model()


class InvoiceQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("billing.view_invoice"):
            # print('user.is_staff and has_perm')
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            # print('User.objects.filter(supervisor=user).exists()')
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(created_by__id=user.id) | Q(created_by__id__in=user_team_ids)
            )
        elif user.is_commercial:
            # print('user.is_commercial')
            return self.filter(Q(created_by__id=user.id))
        else:
            return self.none()


class QuoteQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_staff and user.has_perm("billing.view_quote"):
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(created_by__id=user.id) | Q(created_by__id__in=user_team_ids)
            )
        elif user.is_commercial:
            return self.filter(Q(created_by__id=user.id))
        else:
            return self.none()


class AbstractBill(CRUDUrlMixin, TimestampedModel):
    bill_number = models.CharField(max_length=50, verbose_name=_("Numéro"), unique=True)
    # company = models.ForeignKey('crm.Company', on_delete=models.PROTECT, related_name='%(class)ss')
    lead = models.ForeignKey(
        "leads.B2BLead",
        on_delete=models.PROTECT,
        related_name="%(class)ss",
        verbose_name=_("Opportunité"),
        null=True,
        blank=True,
    )

    due_date = models.DateField(
        verbose_name=_("Date d'échéance"), null=True, blank=True
    )
    creation_date = models.DateField(_("Creation date"), default=date.today)
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Montant total"))

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_updated"
    )
    notes = models.TextField(blank=True, null=True)
    bill_total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Montant total"), blank=True, null=True,
        help_text=_("Applicable seulement si vous ne souhaitez pas utiliser les lignes de facture.")
        
    )
    bill_discount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Remise"), blank=True, null=True,
        help_text=_("Remise sur le total de la facture.")
    )
    class Meta:
        abstract = True

    def generate_bill_number(self, year=None, prefix=""):
        """
        Generates a unique bill number for the given year and optional prefix.
        Format: <prefix><year>-<sequence>
        Example: INV2024-001
        """
        if year is None:
            year = now().year
        # Find the last bill for the year and prefix
        last_bill = (
            self.__class__.objects.filter(
                bill_number__startswith=f"{prefix}{year}-", creation_date__year=year
            )
            .order_by("-bill_number")
            .first()
        )
        if last_bill and last_bill.bill_number:
            import re

            match = re.match(rf"^{prefix}{year}-(\d+)$", last_bill.bill_number)
            if match:
                sequence = int(match.group(1)) + 1
            else:
                sequence = 1
        else:
            sequence = 1
        return f"{prefix}{year}-{sequence:03d}"

    @property
    def num_of_days_to_due(self):
        if self.due_date:
            return (self.due_date - now().date()).days
        return None

    @property
    def get_due_date_with_number_of_days(self):
        if self.due_date:
            return f"{self.due_date} ({self.num_of_days_to_due} jours)"
        return None

    @property
    def get_total_ttc(self):
        total_amount = sum(item.get_total_item for item in self.lines.all())
        return total_amount or self.bill_total or 0


    @property
    def get_total_net(self):
        total_net = self.get_total_ttc / (
            1 + sum(tax.tax / 100 for tax in Tax.objects.filter(is_active=True))
        )
        return total_net


class Quote(AbstractBill):
    class States(models.IntegerChoices):
        PENDING = 1, _("En attente")
        SENT = 2, _("Envoyé")
        ACCEPTED = 3, _("Accepté")
        REFUSED = 4, _("Refusé")
        CANCELED = 5, _("Annulé")  # how should we handle CANCELED?

    state = models.PositiveSmallIntegerField(
        choices=States.choices, default=States.PENDING, verbose_name=_("Status")
    )
    expiration_date = models.DateField(_("date d'expiration"), null=True, blank=True)
    objects = QuoteQueryset.as_manager()

    class Meta:
        verbose_name = _("Devis")
        verbose_name_plural = _("Devis")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.bill_number} - {self.lead}"

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("billing:bulk_delete_quotes")

    def get_absolute_url(self):
        return reverse("billing:detail_quote", kwargs={"pk": self.pk})

    def convert_to_invoice(self):

        invoice = Invoice(
            due_date=self.due_date,
            lead=self.lead,
            creation_date=self.creation_date,
            created_by=self.created_by,
            updated_by=self.updated_by,
            notes=self.notes,
            state=Invoice.States.PENDING,  # Set initial state for the invoice
        )
        invoice.save()
        print("invoice created:>>>>>>>>>>>>>>>>>>>>>>>>>>>>><", invoice)
        return invoice

    @property
    def get_state_color(self):
        state = self.state
        if state == 1:  # PENDING
            return "warning"
        elif state == 2:  # SENT
            return "info"
        elif state == 3:  # ACCEPTED
            return "success"
        elif state == 4:  # REFUSED
            return "danger"
        elif state == 5:  # CANCELED
            return "dark"
        else:
            return None


class Invoice(AbstractBill):
    class States(models.IntegerChoices):
        PENDING = 1, _("En attente")
        SENT = 2, _("Envoyé")
        PARTIAL = 3, _("Partiellement payé")
        PAID = 4, _("Payé")
        CANCELED = 5, _("Annulé")  # how should we handle CANCELED?

    state = models.PositiveSmallIntegerField(
        choices=States.choices, default=States.PENDING, verbose_name=_("Status")
    )
    objects = InvoiceQueryset.as_manager()

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.bill_number}"

    @property
    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def rest_amount(self):
        return self.get_total_ttc - self.paid_amount

    @property
    def payment_date(self):
        return self.payments.first().date if self.payments.exists() else None

    def payment_wait(self):
        """Time between payment and due date"""
        if self.payment_date:
            wait = self.payment_date - self.due_date
        else:
            wait = date.today() - self.due_date
        return wait.days

    def payment_delay(self):
        """Time between creation and payment"""
        if self.payment_date:
            wait = self.payment_date - self.creation_date
        else:
            wait = date.today() - self.creation_date
        return wait.days

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("billing:bulk_delete_invoices")

    def get_absolute_url(self):
        return reverse("billing:detail_invoice", kwargs={"pk": self.pk})

    @property
    def get_state_color(self):
        state = self.state
        if state == 1:  # PENDING
            return "warning"
        elif state == 2:  # SENT
            return "info"
        elif state == 3:  # PARTIAL
            return "primary"
        elif state == 4:  # PAID
            return "success"
        elif state == 5:  # CANCELED
            return "danger"
        else:
            return None


class BillLine(TimestampedModel):
    # class Discount(models.IntegerChoices):
    #     PERCENT     = 1, _('Percent'),
    #     LINE_AMOUNT = 2, _('Amount per line'),
    #     ITEM_AMOUNT = 3, _('Amount per unit'),

    title = models.CharField(max_length=200, verbose_name=_("Titre"), blank=True, null=True)
    quantity = models.PositiveIntegerField(
        default=1, verbose_name=_("Quantité"), blank=True, null=True
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Prix"), blank=True, null=True
    )
    unit = models.CharField(
        max_length=50, verbose_name=_("Unité"), blank=True, null=True
    )
    discount = models.DecimalField(
        _("Remise"),
        help_text=_("Réduction sur le total de la ligne"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Prix total"), default=0
    )
        
    # description = HTMLField(
    #     max_length=255, verbose_name=_("Description"), blank=True, null=True
    # )
    description = models.CharField(
        max_length=255, verbose_name=_("Description"), blank=True, null=True
    )
    display_order = models.PositiveIntegerField(
        default=0, verbose_name=_("Ordre d'affichage")
    )

    def save(self, *args, **kwargs):
        self.total_price = (self.quantity or 1) * ( self.unit_price or 0)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Client Bill Line")
        verbose_name_plural = _("Client Bill Lines")
        ordering = ["bill", "description"]
        abstract = True

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"

    @property
    def get_total_item(self):
        return self.total_price - (self.discount or 0)


class InvoiceItem(BillLine):
    """
    Ligne de facture pour une facture
    """

    bill = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")

    class Meta:
        verbose_name = _("Invoice Item")
        verbose_name_plural = _("Invoice Items")
        ordering = ["bill", "display_order"]


class QuoteItem(BillLine):
    """
    Ligne de devis pour un devis
    """

    bill = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")

    class Meta:
        verbose_name = _("Quote Item")
        verbose_name_plural = _("Quote Items")
        ordering = ["bill", "display_order"]

    def convert_to_invoice_item(self, invoice):
        """
        Convert this quote item to an invoice item.
        This method creates a new InvoiceItem instance with the same details as this quote item.
        """
        invoice_item = InvoiceItem(
            bill=invoice,
            title=self.title,
            quantity=self.quantity,
            unit_price=self.unit_price,
            unit=self.unit,
            discount=self.discount,
            description=self.description,
            display_order=self.display_order,
        )
        invoice_item.save()
        print("invoice item created:>>>>>>>>>>>>>>>>>>>>>>>>>>>>><", invoice_item)
        return invoice_item
