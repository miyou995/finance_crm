from django.contrib import admin

# Register your models here.


from apps.crm.models import (
    Contact,
    ContactEmail,
    ContactPhone,
    Company,
    CompanyEmail,
    CompanyPhone,
)
from apps.crm.models.company import ActivitySector

# Register your models here.


class ContactEmailInline(admin.TabularInline):
    model = ContactEmail


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")
    list_display_links = ("full_name",)
    search_fields = (
        "id",
        "full_name",
    )
    inlines = [ContactEmailInline, ContactPhoneInline]


class CompanyEmailInline(admin.TabularInline):
    model = CompanyEmail


class CompanyPhoneInline(admin.TabularInline):
    model = CompanyPhone


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    list_display_links = ("name",)
    search_fields = ("id", "name", "slug")
    inlines = [CompanyEmailInline, CompanyPhoneInline]

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related('lead_source')


@admin.register(ActivitySector)
class ActivitySectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
