import logging
from django.dispatch import receiver
from apps.billing.models import Bill, Invoice
from django.db.models.signals import post_save, post_delete
from apps.transactions.models import (
    ClientPayment,
    LedgerEntry,
    MiscTransaction,
    StaffPayment,
)



def create_ledger_entry_signal(sender, instance, created, **kwargs):
    if created:
        try:
            # Create a new ledger entry based on the subscription payment
            new_entry = LedgerEntry(
                # user=instance.created_by,
                amount=instance.amount,
                created_by=str(instance.created_by),
                # date=instance.date,
            )

            
            if isinstance(instance, ClientPayment):
                new_entry.client_payment = instance
                new_entry.entry_type = "income"
                new_entry.description = (
                    f"{instance.bill.lead.company} {instance.bill.bill_number}"
                )

            elif isinstance(instance, StaffPayment):
                new_entry.staff_payment = instance
                new_entry.entry_type = "expense"
                new_entry.description = f"{instance.staff_member.full_name}"

            elif isinstance(instance, MiscTransaction):
                new_entry.misc_transaction = instance
                new_entry.entry_type = (
                    "income"
                    if instance.transaction_type == instance.TransactionType.INCOME
                    else "expense"
                )
                new_entry.description = f"{instance.title}"

            new_entry.save()

        except Exception as e:
            instance.delete()
            logging.error(f"Error creating ledger entry: {e}")


post_save.connect(create_ledger_entry_signal, sender=ClientPayment)
post_save.connect(create_ledger_entry_signal, sender=StaffPayment)
post_save.connect(create_ledger_entry_signal, sender=MiscTransaction)


@receiver(post_save, sender=ClientPayment)
def change_invoice_state_paid(sender, instance, **kwargs):
    if instance.bill and instance.bill.rest_amount == 0:
        instance.bill.state = Bill.BillStates.PAID
        print("------------------>>>>>>>>Invoice is fully paid, changing state to PAID")
        instance.bill.save()


@receiver(post_delete, sender=ClientPayment)
def change_invoice_state_unpaid(sender, instance, **kwargs):
    print("pre_delete signal triggered for ClientPayment")
    # if instance.bill and instance.bill.rest_amount > 0:
    #     print("Invoice is not fully paid, changing state to PENDING")
    #     instance.bill.state = Bill.BillStates.PENDING
    #     instance.bill.save()
