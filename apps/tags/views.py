from django.contrib.auth.mixins import PermissionRequiredMixin
from apps.core.mixins import BaseManageHtmxFormView, DeleteMixinHTMX
from apps.tags.forms import TagsModelForm
from apps.tags.models import Tags
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView

from apps.tags.tables import TagsHTMxTable


# Create your views here.


class ManageSalleHtmx(BaseManageHtmxFormView):
    permission_required = "tags.add_tags"
    form_class = TagsModelForm
    model = Tags
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class SalleDeleteHTMX(DeleteMixinHTMX):
    permission_required = "tags.delete_tags"
    model = Tags


class TagsListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "tags.view_tags"
    model = Tags

    template_name = "tables/table_partial.html"
    filterset_class = None
    table_class = TagsHTMxTable

    def get_queryset(self):
        return Tags.objects.all().order_by("name")
