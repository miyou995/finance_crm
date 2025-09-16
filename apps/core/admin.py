from django.contrib import admin

# Register your models here.
from .models import Tax, LeadSource


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "tax", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("-created_at",)


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
