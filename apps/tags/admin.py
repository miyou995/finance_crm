from django.contrib import admin

from .models import Tags


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    list_filter = ("created_at", "updated_at")

    def __str__(self):
        return self.name
