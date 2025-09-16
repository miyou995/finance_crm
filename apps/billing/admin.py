from django.contrib import admin
from apps.billing.models import InvoiceItem, Quote, Invoice, QuoteItem

# Register your models here.


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "state", "created_at")
    # search_fields = ('customer__name',)
    list_filter = ("created_at",)
    inlines = [QuoteItemInline]


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "created_at")
    # search_fields = ('customer__name',)
    list_filter = ("created_at",)
    inlines = [InvoiceItemInline]


# @admin.register(BillLine)
# class BillLineAdmin(admin.ModelAdmin):
#     list_display = ('id', 'description', 'quantity', 'unit_price', 'total')
#     search_fields = ('description',)


# @admin.register(InvoiceItem)
# class InvoiceItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'bill','description', 'quantity', 'unit_price', )
#     search_fields = ('description',)


# @admin.register(QuoteItem)
# class QuoteItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'bill', 'description', 'quantity', 'unit_price', )
#     search_fields = ('description', )
