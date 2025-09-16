from django.contrib import admin

# Register your models here.
from .models import B2BLead, B2CLead, B2BLeadState, B2CLeadState


class B2BLeadStateInline(admin.TabularInline):
    model = B2BLeadState
    extra = 1


class B2CLeadStateInline(admin.TabularInline):
    model = B2CLeadState
    extra = 1


@admin.register(B2BLead)
class B2BLeadAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "created_at", "updated_at")
    inlines = [B2BLeadStateInline]


@admin.register(B2CLead)
class B2CLeadAdmin(admin.ModelAdmin):
    list_display = ("title", "contact", "created_at", "updated_at")
    inlines = [B2CLeadStateInline]
