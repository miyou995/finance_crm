from datetime import date

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel

User = get_user_model()


class ClientPaymentQuerySet(models.QuerySet):
    def search(self, query):
        if query:
            return self.filter(
                Q(amount__icontains=query)
                | Q(invoice__bill_number__icontains=query)
                | Q(invoice__lead__company__name__icontains=query)
            ).distinct()
        return self

    def limit_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_staff and user.has_perm("billing.view_invoicepayment"):
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(invoice__lead__users__in=[user.id])
                | Q(invoice__lead__users__in=user_team_ids)
            ).distinct()
        elif user.is_commercial:
            return self.filter(Q(invoice__lead__users__in=[user.id])).distinct()
        else:
            return self.none()


class Journal(models.Model):
    """Equivalent to Odoo's accounting journal (bank, cash, etc.)."""
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=[("bank", "Bank"), ("cash", "Cash"), ("other", "Other")],
        default="bank",
    )

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name



class Transaction(CRUDUrlMixin, TimestampedModel):
    class PAYMENT_METHOD(models.TextChoices):  # should be moove to payment
        CASH = "cash", _("Cash")
        BANK_TRANSFER = "bank_transfer", _("Virement bancaire")
        PAYMENT_CARD = "payment_card", _("Carte de paiement")

    payment_method = models.CharField(
        _("payment method"),
        choices=PAYMENT_METHOD.choices,
        default=PAYMENT_METHOD.CASH,
        max_length=64,
    )
    
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT, related_name="%(class)ss", null=True, blank=True)

    amount = models.DecimalField(
        max_digits=11,
        verbose_name=_("Montant"),
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    date = models.DateField(default=date.today)

    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name=_("Updated by"),
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )
    reference = models.CharField(max_length=200, blank=True, null=True)


    notes = models.TextField(blank=True, null=True)

    # objects = TransactionQuerySet.as_manager()
    class Meta:
        ordering = ["-date"]
        abstract = True

    def __str__(self):
        return f"{self.__class__._meta.verbose_name}: {self.amount} on {self.date}"


class StaffPayment(Transaction):
    staff_member = models.ForeignKey(
        User,
        related_name="staff_payments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Membre du personnel"
    )

    class Meta(Transaction.Meta):
        verbose_name = _("Paiement Personnel")
        verbose_name_plural = _("Paiements Personnels")

    @classmethod
    def get_create_url(cls):
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    def get_delete_url(self):
        return reverse(
            f"{self._meta.app_label}:delete_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("transactions:bulk_delete_staffpayment")

    @classmethod
    def get_export_url(cls):
        return reverse("transactions:export_staffpayment")


class ClientPayment(Transaction):
    client = models.ForeignKey(
        "crm.Company", on_delete=models.PROTECT, related_name="payments"
    )
    invoice = models.ForeignKey(
        "billing.Invoice", on_delete=models.PROTECT, related_name="payments", null=True, blank=True
    )

    
    objects = ClientPaymentQuerySet.as_manager()

    class Meta(Transaction.Meta):
        verbose_name = _("Paiement Facture")
        verbose_name_plural = _("Paiements Facture")

    @property
    def invoice_remaining_amount(self):
        return self.invoice.get_total_ttc - self.invoice.paid_amount

    # @classmethod
    # def get_create_url(cls):
    #     return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    @classmethod
    def get_create_url(cls, company_pk=None, invoice_pk=None):
        if company_pk:
            return reverse(
                f"{cls._meta.app_label}:create_company_invoicepayment",
                kwargs={"company_pk": company_pk},
            )
        elif invoice_pk:
            return reverse(
                f"{cls._meta.app_label}:create_invoice_invoicepayment",
                kwargs={"invoice_pk": invoice_pk},
            )
        else:
            return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("transactions:bulk_delete_invoicepayment")

    @classmethod
    def get_export_url(cls):
        return reverse("transactions:export_invoicepayment")


class PaymentInvoice(models.Model):
    payment = models.ForeignKey(ClientPayment, on_delete=models.CASCADE)
    invoice = models.ForeignKey("billing.Invoice", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class MiscTransaction(Transaction):
    """
    Model for miscellaneous transactions that are not directly related to subscriptions or payments.
    This can include one-time payments, refunds, or other financial transactions that need to be tracked
    """

    class TransactionType(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")
        REFUND = "refund", _("Refund")

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name="Description")
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, default=TransactionType.INCOME
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        related_name="misc_transactions",
        blank=True,
        null=True,
    )

    class Meta(Transaction.Meta):
        verbose_name = _("Autre Transaction")
        verbose_name_plural = _("Autres Transactions")

    def is_income(self):
        return self.transaction_type == self.TransactionType.INCOME

    def is_expense(self):
        return self.transaction_type == self.TransactionType.EXPENSE

    def is_refund(self):
        return self.transaction_type == self.TransactionType.REFUND

    def get_delete_url(self):
        return reverse(
            f"{self._meta.app_label}:delete_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("transactions:bulk_delete_misctransaction")

    @property
    def get_transaction_color(self):
        return "success" if self.is_income() else "danger"

    @classmethod
    def get_export_url(cls):
        return reverse("transactions:export_misctransaction")


class Expense(MiscTransaction, CRUDUrlMixin):
    class Meta(Transaction.Meta):
        proxy = True  # This allows Expense to inherit from MiscTransaction without creating a new table
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")

    def save(self, *args, **kwargs):
        print("SALIIII")
        self.transaction_type = self.TransactionType.EXPENSE
        super().save(*args, **kwargs)

    @classmethod
    def get_create_url(cls, contact_pk=None):
        if contact_pk:
            return reverse(
                f"{cls._meta.app_label}:create_contact_expense",
                kwargs={"contact_pk": contact_pk},
            )
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")


class Income(MiscTransaction, CRUDUrlMixin):
    class Meta(Transaction.Meta):
        proxy = True  # This allows Income to inherit from MiscTransaction without creating a new table
        verbose_name = _("Income")
        verbose_name_plural = _("Incomes")

    def save(self, *args, **kwargs):
        self.transaction_type = self.TransactionType.INCOME
        super().save(*args, **kwargs)

    @classmethod
    def get_create_url(cls, contact_pk=None):
        if contact_pk:
            return reverse(
                f"{cls._meta.app_label}:create_contact_income",
                kwargs={"contact_pk": contact_pk},
            )
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")


class LedgerEntry(TimestampedModel,CRUDUrlMixin):
    class EntryType(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")

    created_by = models.CharField(
        max_length=100, help_text=_("User who created this entry")
    )
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    amount = models.DecimalField(
        max_digits=11, decimal_places=2, validators=[MinValueValidator(0)]
    )

    account = models.CharField(
        max_length=100,
        help_text=_("Account name affected by this entry (e.g., Cash, Revenue)"),
    )

    client_payment = models.ForeignKey(
        ClientPayment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ledger_entries",
    )
    staff_payment = models.ForeignKey(
        StaffPayment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ledger_entries",
    )
    misc_transaction = models.ForeignKey(
        MiscTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ledger_entries",
    )


    class Meta:
        verbose_name = _("Ledger Entry")
        verbose_name_plural = _("Ledger Entries")
        ordering = ["-date"]
        constraints = [
            models.CheckConstraint(
                condition=(
                      Q(client_payment__isnull=False, staff_payment__isnull=True, misc_transaction__isnull=True)
                    | Q(client_payment__isnull=True, staff_payment__isnull=False, misc_transaction__isnull=True)
                    | Q(client_payment__isnull=True, staff_payment__isnull=True, misc_transaction__isnull=False)
                    | Q(client_payment__isnull=True, staff_payment__isnull=True, misc_transaction__isnull=True)
                ),
                name="exactly_one_transaction_fk",
            ),
        ]


    def __str__(self):
        return f"{self.date} {self.get_entry_type_display()}: {self.amount} → {self.account}"

    def get_transaction_type(self):
        if self.client_payment:
            return self.client_payment._meta.verbose_name

        elif self.staff_payment:
            return self.staff_payment._meta.verbose_name
 
        elif self.misc_transaction:
            return self.misc_transaction._meta.verbose_name
        # return "unknown"

    def get_user_url(self):
        if self.client_payment:
            return self.client_payment.get_contact_url()

        elif self.staff_payment:
            return reverse("crm:detail_contact", kwargs={"pk": self.staff_member.pk})
        elif self.misc_transaction and self.misc_transaction.contact:
            return reverse(
                "crm:detail_contact", kwargs={"pk": self.misc_transaction.contact.pk}
            )
        return False

    @property
    def get_transaction_color(self):
        return "success" if self.entry_type == self.EntryType.INCOME else "danger"

    @classmethod
    def get_export_url(cls):
        return reverse("transactions:export_ledger")
