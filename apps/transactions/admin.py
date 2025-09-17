from django.contrib import admin
from .models import (
    MiscTransaction,
    StaffPayment,
    ClientPayment,
    LedgerEntry,
)

# Register your models here.

@admin.register(MiscTransaction)
class MiscTransactionAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "date", "transaction_type", "contact")
    search_fields = ("title",)
    list_filter = ("date",)
    ordering = ("-date",)
    list_per_page = 20



@admin.register(StaffPayment)
class StaffPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "staff_member",
        "amount",
        "date",
    )
    search_fields = (
        "staff_member__last_name",
        "staff_member__first_name",
    )
    list_filter = ("date",)
    ordering = ("-date",)
    list_per_page = 20


@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "bill",
        "bill__bill_number",
        "amount",
        "date",
    )
    search_fields = ("bill__bill_number",)
    list_filter = ("date",)
    ordering = ("-date",)
    list_per_page = 20


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "description", "entry_type", "account")
    list_filter = ("date", "entry_type")
    ordering = ("-date",)
    list_per_page = 100
