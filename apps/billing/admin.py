from django.contrib import admin
from apps.billing.models import BillLine, Quote, Invoice

# Register your models here.


class BillLineInline(admin.TabularInline):
    model = BillLine
    fk_name = "bill"

    extra = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "state", "created_at")
    list_filter = ("created_at",)
    inlines = [BillLineInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "created_at")
    list_filter = ("created_at",)
    inlines = [BillLineInline]

