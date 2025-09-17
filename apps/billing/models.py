import re
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, Tax, TimestampedModel

User = get_user_model()


class BillQuerySet(models.QuerySet):
    def invoices(self):
        return self.filter(bill_type="invoice")

    def quotes(self):
        return self.filter(bill_type="quote")

    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("billing.view_bill"):
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


class BillType(models.TextChoices):
    QUOTE = "quote", _("Devis")
    INVOICE = "invoice", _("Facture")
    CREDIT_NOTE = "credit_note", _("Avoir")
    OTHER = "other", _("Autre")



    
    
    
class Bill(CRUDUrlMixin, TimestampedModel):
    
    class BillStates(models.IntegerChoices):
        PENDING = 1, _("En attente")
        SENT = 2, _("Envoyé")
        ACCEPTED = 3, _("Accepté")
        REFUSED = 4, _("Refusé")
        
        PARTIAL = 5, _("Partiellement payé")
        PAID = 6, _("Payé")
        CANCELED = 7, _("Annulé")
    bill_type = models.CharField(
        max_length=20,
        choices=BillType.choices,
        default=BillType.QUOTE,
        verbose_name=_("Type de facture"),
    )
    bill_number = models.CharField(max_length=50, verbose_name=_("Numéro"))
    bill_year = models.PositiveIntegerField(editable=False, db_index=True)
    lead = models.ForeignKey(
        "leads.B2BLead",
        on_delete=models.PROTECT,
        related_name="bills",
        verbose_name=_("Opportunité"),
        null=True,
        blank=True,
    )
    due_date = models.DateField(verbose_name=_("Date d'échéance"), null=True, blank=True)
    creation_date = models.DateField(_("Creation date"), default=date.today)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bills_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bills_updated",
    )
    notes = models.TextField(blank=True, null=True)
    bill_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Montant total"),
        blank=True,
        null=True,
        help_text=_(
            "Applicable seulement si vous ne souhaitez pas utiliser les lignes de facture."
        ),
    )
    bill_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Remise"),
        blank=True,
        null=True,
        help_text=_("Remise sur le total de la facture."),
    )
    state = models.PositiveSmallIntegerField(choices=BillStates.choices, default=BillStates.PENDING, verbose_name=_("Statut"), null=True, blank=True)
    expiration_date = models.DateField(_("date d'expiration"), null=True, blank=True)

    objects = BillQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["bill_type", "bill_year", "bill_number"],
                name="unique_bill_number_per_type_year",
            )
        ]

    def save(self, *args, **kwargs):
        if self.creation_date:
            self.bill_year = self.creation_date.year
        else:
            self.bill_year = now().year
        super().save(*args, **kwargs)

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


    def generate_bill_number(self, year=None, prefix=""):
        if year is None:
            year = now().year
        prefix = prefix or ""
        pattern = f"{prefix}{year}-"
        last_bill = (
            Bill.objects.filter(
                bill_type=self.bill_type,
                bill_year=year,
                bill_number__startswith=pattern,
            )
            .order_by("-bill_number")
            .first()
        )
        if last_bill and last_bill.bill_number:
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

    # @property
    # def lines(self):
    #     if self.bill_type == BillType.INVOICE:
    #         return self.invoice_items
    #     if self.bill_type == BillType.QUOTE:
    #         return self.quote_items
    #     return self.invoice_items.none()
    
    @property
    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())
    @property
    def rest_amount(self):
        return self.get_total_ttc - self.paid_amount

    @property
    def get_total_ttc(self):
        total_amount = sum(item.get_total_item for item in self.lines.all())
        return total_amount or self.bill_total or 0

    @property
    def get_total_net(self):
        taxes = sum(tax.tax / 100 for tax in Tax.objects.filter(is_active=True))
        if taxes:
            return self.get_total_ttc / (1 + taxes)
        return self.get_total_ttc


# class Quote(AbstractBill):
#     class States(models.IntegerChoices):
#         PENDING = 1, _("En attente")
#         SENT = 2, _("Envoyé")
#         ACCEPTED = 3, _("Accepté")
#         REFUSED = 4, _("Refusé")
#         CANCELED = 5, _("Annulé")  # how should we handle CANCELED?

#     state = models.PositiveSmallIntegerField(
#         choices=States.choices, default=States.PENDING, verbose_name=_("Status")
#     )
#     expiration_date = models.DateField(_("date d'expiration"), null=True, blank=True)
#     objects = QuoteQueryset.as_manager()

#     class Meta:
#         verbose_name = _("Devis")
#         verbose_name_plural = _("Devis")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.bill_number} - {self.lead}"

#     @classmethod
#     def get_bulk_delete_url(cls):
#         return reverse("billing:bulk_delete_quotes")

#     def get_absolute_url(self):
#         return reverse("billing:detail_quote", kwargs={"pk": self.pk})

#     def convert_to_invoice(self):
#         invoice = Invoice(
#             due_date=self.due_date,
#             lead=self.lead,
#             creation_date=self.creation_date,
#             created_by=self.created_by,
#             updated_by=self.updated_by,
#             notes=self.notes,
#             state=Bill.BillStates.PENDING,  # Set initial state for the invoice
#         )
#         invoice.save()
#         print("invoice created:>>>>>>>>>>>>>>>>>>>>>>>>>>>>><", invoice)
#         return invoice

#     @property
#     def get_state_color(self):
#         state = self.state
#         if state == 1:  # PENDING
#             return "warning"
#         elif state == 2:  # SENT
#             return "info"
#         elif state == 3:  # ACCEPTED
#             return "success"
#         elif state == 4:  # REFUSED
#             return "danger"
#         elif state == 5:  # CANCELED
#             return "dark"
#         else:
#             return None


# class Invoice(AbstractBill):
#     class States(models.IntegerChoices):
#         PENDING = 1, _("En attente")
#         SENT = 2, _("Envoyé")
#         PARTIAL = 3, _("Partiellement payé")
#         PAID = 4, _("Payé")
#         CANCELED = 5, _("Annulé")  # how should we handle CANCELED?

#     state = models.PositiveSmallIntegerField(
#         choices=States.choices, default=States.PENDING, verbose_name=_("Status")
#     )
#     objects = InvoiceQueryset.as_manager()

#     class Meta:
#         verbose_name = _("Facture")
#         verbose_name_plural = _("Factures")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.bill_number}"

#     @property
#     def paid_amount(self):
#         return sum(payment.amount for payment in self.payments.all())

#     @property
#     def rest_amount(self):
#         return self.get_total_ttc - self.paid_amount

#     @property
#     def payment_date(self):
#         return self.payments.first().date if self.payments.exists() else None

#     def payment_wait(self):
#         """Time between payment and due date"""
#         if self.payment_date:
#             wait = self.payment_date - self.due_date
#         else:
#             wait = date.today() - self.due_date
#         return wait.days

#     def payment_delay(self):
#         """Time between creation and payment"""
#         if self.payment_date:
#             wait = self.payment_date - self.creation_date
#         else:
#             wait = date.today() - self.creation_date
#         return wait.days

#     @classmethod
#     def get_bulk_delete_url(cls):
#         return reverse("billing:bulk_delete_invoices")

#     def get_absolute_url(self):
#         return reverse("billing:detail_invoice", kwargs={"pk": self.pk})

#     @property
#     def get_state_color(self):
#         state = self.state
#         if state == 1:  # PENDING
#             return "warning"
#         elif state == 2:  # SENT
#             return "info"
#         elif state == 3:  # PARTIAL
#             return "primary"
#         elif state == 4:  # PAID
#             return "success"
#         elif state == 5:  # CANCELED
#             return "danger"
#         else:
#             return None





class InvoiceQueryset(models.QuerySet):
    def get_queryset(self):
        return super().get_queryset().filter(bill_type=BillType.INVOICE)
    def limit_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.is_staff and user.has_perm("billing.view_invoice"):
            return self.all()
        if User.objects.filter(supervisor=user).exists():
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(created_by__id=user.id) | Q(created_by__id__in=user_team_ids)
            )
        if getattr(user, "is_commercial", False):
            return self.filter(Q(created_by__id=user.id))
        return self.none()


class QuoteQueryset(models.QuerySet):
    def get_queryset(self):
        return super().get_queryset().filter(bill_type=BillType.QUOTE)
    def limit_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.is_staff and user.has_perm("billing.view_quote"):
            return self.all()
        if User.objects.filter(supervisor=user).exists():
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(created_by__id=user.id) | Q(created_by__id__in=user_team_ids)
            )
        if getattr(user, "is_commercial", False):
            return self.filter(Q(created_by__id=user.id))
        return self.none()


class Invoice(Bill):

    objects = InvoiceQueryset.as_manager()

    class Meta:
        proxy = True
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.bill_type = BillType.INVOICE
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_number}"

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("billing:bulk_delete_invoices")

    def get_absolute_url(self):
        return reverse("billing:detail_invoice", kwargs={"pk": self.pk})



class Quote(Bill):
    objects = QuoteQueryset.as_manager()

    class Meta:
        proxy = True
        verbose_name = _("Devis")
        verbose_name_plural = _("Devis")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.bill_type = BillType.QUOTE
        super().save(*args, **kwargs)

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
            bill_total=self.bill_total,
            bill_discount=self.bill_discount,
        )
        invoice.save()
        for item in self.lines.all():
            item.clone_to_bill(invoice)
        return invoice




class BillLine(TimestampedModel):
    # class Discount(models.IntegerChoices):
    #     PERCENT     = 1, _('Percent'),
    #     LINE_AMOUNT = 2, _('Amount per line'),
    #     ITEM_AMOUNT = 3, _('Amount per unit'),
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="lines")

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
        verbose_name = _("Bill Line")
        verbose_name_plural = _("Bill Lines")
        ordering = ["bill", "description"]

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"

    @property
    def get_total_item(self):
        return self.total_price - (self.discount or 0)


# class InvoiceItem(BillLine):
#     """
#     Ligne de facture pour une facture
#     """


#     class Meta:
#         verbose_name = _("Invoice Item")
#         verbose_name_plural = _("Invoice Items")
#         ordering = ["bill", "display_order"]


# class QuoteItem(BillLine):
#     """
#     Ligne de devis pour un devis
#     """

#     bill = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")

#     class Meta:
#         verbose_name = _("Quote Item")
#         verbose_name_plural = _("Quote Items")
#         ordering = ["bill", "display_order"]

#     def convert_to_invoice_item(self, invoice):
#         """
#         Convert this quote item to an invoice item.
#         This method creates a new InvoiceItem instance with the same details as this quote item.
#         """
#         invoice_item = InvoiceItem(
#             bill=invoice,
#             title=self.title,
#             quantity=self.quantity,
#             unit_price=self.unit_price,
#             unit=self.unit,
#             discount=self.discount,
#             description=self.description,
#             display_order=self.display_order,
#         )
#         invoice_item.save()
#         print("invoice item created:>>>>>>>>>>>>>>>>>>>>>>>>>>>>><", invoice_item)
#         return invoice_item
