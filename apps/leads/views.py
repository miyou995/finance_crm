from django.views import View
from django_filters.views import FilterView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_tables2 import SingleTableMixin
from apps.core.mixins import (
    BaseManageHtmxFormView,
    BreadcrumbMixin,
    BulkDeleteMixinHTMX,
    DeleteMixinHTMX,
    ExportDataMixin,
    ImportDataMixin,
)
from apps.leads.filters import B2bLeadFilter, B2cLeadFilter
from apps.leads.forms import B2bLeadModelForm, B2cLeadModelForm
from apps.leads.models import B2BLead, B2BLeadState, B2CLead, B2CLeadState, States
from apps.leads.tables import (
    B2BLeadStateTable,
    B2bHtmxLeadTable,
    B2cHtmxLeadTable,
)

######################### B2B Leads Views #########################


class BaseContext(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "leads.view_b2blead"
    # status = "all"

    def get_queryset(self):
        queryset = self.model.limit_user(self.request.user).objects.all()
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["export_url"] = self.model.get_export_url()
        context["import_url"] = self.model.get_import_url()

        context["bulk_delete_url"] = self.model.get_bulk_delete_url()

        # print('\n \n \n \n \n \n self.status', self.status.name.lower())

        if self.status:
            context["b2b_lead_url"] = reverse(
                f"leads:{self.status.name.lower()}_b2b_lead_list"
            )
            context["b2c_lead_url"] = reverse(
                f"leads:{self.status.name.lower()}_b2c_lead_list"
            )
        else:
            context["b2b_lead_url"] = reverse("leads:all_b2b_lead_list")
            context["b2c_lead_url"] = reverse("leads:all_b2c_lead_list")

        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["lead_list.html"]



class B2BLeadStateUserView(BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = 'leads.view_b2blead'

    model = B2BLeadState
    table_class = B2BLeadStateTable
    paginate_by = 20
    filterset_class = B2bLeadFilter
    template_name = "tables/table_partial.html"

    def get_queryset(self):
        queryset = self.model.objects.limit_user(self.request.user).all()
        user_id = self.kwargs.get("pk")
        return queryset.filter(created_by=user_id).order_by("-created_at")


class B2CLeadStateUserView(B2BLeadStateUserView):

    permission_required = 'leads.view_b2clead'

    model = B2CLeadState


class B2bLeadListView(
    BreadcrumbMixin, BaseContext, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    model = B2BLead
    table_class = B2bHtmxLeadTable
    paginate_by = 20
    filterset_class = B2bLeadFilter
    status = None

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["import_fields_url"] = reverse('leads:import_fields_b2b_lead')
    #     return context

    def get_queryset(self):
        queryset = self.model.objects.limit_user(self.request.user).all()
        if self.status:
            queryset = queryset.filter(current_state=self.status)
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_table_kwargs(self):
        return {"company_pk": self.kwargs.get("pk")}


class B2cLeadListView(BaseContext, SingleTableMixin, FilterView):
    # permission_required = 'leads.view_b2clead'
    model = B2CLead
    table_class = B2cHtmxLeadTable
    paginate_by = 20
    filterset_class = B2cLeadFilter

    status = None  # Default status, can be overridden in subclasses

    def get_queryset(self):
        queryset = self.model.objects.limit_user(self.request.user).all()
        if self.status:
            queryset = queryset.filter(current_state=self.status)
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs


class CompanyB2bLeadsTable(B2bLeadListView):
    status = None

    def get_queryset(self):
        queryset = super().get_queryset()
        return (
            queryset.limit_user(self.request.user)
            .filter(company__pk=self.kwargs.get("pk"))
            .order_by("-created_at")
        )


# class UserB2BLeadsTable(B2bLeadListView):
#     status = None

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         return queryset.filter(current_state_user__pk=self.kwargs.get('pk')).order_by("-created_at")


class ContactB2cLeadsTable(B2cLeadListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = (
            B2CLead.objects.limit_user(self.request.user)
            .filter(contact__pk=pk)
            .order_by("-created_at")
        )
        return queryset

    def get_table_kwargs(self):
        return {"pk": self.kwargs.get("pk")}


class ManageB2bLeadHTMX(BaseManageHtmxFormView):
    permission_required = "leads.add_b2blead"
    form_class = B2bLeadModelForm
    model = B2BLead
    parent_url_kwarg = "company_pk"

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_b2b_table": None,
    }


# class UserB2CLeadsTable(B2cLeadListView):
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         pk = self.kwargs.get('pk')
#         queryset = B2CLead.objects.limit_user(self.request.user).filter(current_state_user__pk=pk).order_by("-created_at")
#         return queryset


class DeleteB2bLead(DeleteMixinHTMX):
    permission_required = "leads.delete_b2blead"
    model = B2BLead
    htmx_additional_event = "refresh_b2b_table"


class DeleteBulkB2bLeads(BulkDeleteMixinHTMX):
    permission_required = "leads.delete_b2blead"
    model = B2BLead
    htmx_additional_event = "refresh_b2b_table"


class ImportB2bLead(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "leads.add_b2blead"
    model = B2BLead
    fields = [
        "title",
        "company",
        "created_at",
        "created_by",
    ]

    def get_duplicate_check_fields(self):
        return ["title", "company"]


class ImportFieldsB2bLead(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "leads.view_b2blead"
    model = B2BLead
    fields = [
        "title",
        "company",
        "created_at",
        "created_by",
    ]


class ExportB2bLead(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "leads.view_b2blead"
    model = B2BLead
    fields = [
        "title",
        "company",
        "created_at",
        "created_by",
    ]


######################### B2C Leads Views #########################


class ManageB2cLeadHTMX(BaseManageHtmxFormView):
    permission_required = "leads.add_b2clead"
    form_class = B2cLeadModelForm
    model = B2CLead
    parent_url_kwarg = "contact_pk"
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class DeleteB2cLead(DeleteMixinHTMX):
    model = B2CLead


class DeleteBulkB2cLeads(BulkDeleteMixinHTMX):
    permission_required = "leads.delete_b2clead"
    model = B2CLead


class ImportB2cLead(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "leads.add_b2clead"
    model = B2CLead
    fields = [
        "title",
        "contact",
    ]

    def get_duplicate_check_fields(self):
        return ["title", "contact"]


class ExportB2cLead(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "leads.view_b2clead"
    model = B2CLead
    fields = [
        "title",
        "contact",
        "created_at",
    ]


########################## LEADS STATTES ###################################


# >>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<>> New B2B AND B2C Leads View <<<<<<<<<<<<
class NewB2bLeadListView(B2bLeadListView):
    status = States.NEW
    model = B2BLead


class NewB2cLeadListView(B2cLeadListView):
    status = States.NEW
    model = B2CLead


class UntreatedB2bLeadListView(B2bLeadListView):
    status = States.UNTREATED
    model = B2BLead


class UntreatedB2cLeadListView(B2cLeadListView):
    status = States.UNTREATED
    model = B2CLead


class NonInteresseB2bLeadListView(B2bLeadListView):
    status = States.NON_INTERESSE
    model = B2BLead


class NonInteresseB2cLeadListView(B2cLeadListView):
    status = States.NON_INTERESSE
    model = B2CLead


# >>><<<<<<<<<<<<<<<<<<<<>>>>> UNTREATED B2B AND B2C Leads View <<<<<<<<<<<<
class DuplicatedB2bLeadListView(B2bLeadListView):
    status = States.DUPLICATED
    model = B2BLead


class DuplicatedB2cLeadListView(B2cLeadListView):
    status = States.DUPLICATED
    model = B2CLead


# >>>><<<<<<<<<<<<<<<<<<<>>>>> QUALIFIED B2B AND B2C Leads View <<<<<<<<<<<<
class QualifiedB2bLeadListView(B2bLeadListView):
    status = States.QUALIFIED
    model = B2BLead


class QualifiedB2cLeadListView(B2cLeadListView):
    status = States.QUALIFIED
    model = B2CLead


# >>>>>>>><<<<<<<<<<<<<<>> INJOIGNABLE B2B AND B2C Leads View <<<<<<<<<<<<


class InjoignableB2bLeadListView(B2bLeadListView):
    status = States.INJOIGNABLE
    model = B2BLead


class InjoignableB2cLeadListView(B2cLeadListView):
    status = States.INJOIGNABLE
    model = B2CLead


# >>>>>>><<<<<<<<<<<>>> NON QUALIFIED B2B AND B2C Leads View <<<<<<<<<<<<
class NonQualifiedB2bLeadListView(B2bLeadListView):
    status = States.NON_QUALIFIED
    model = B2BLead


class NonQualifiedB2cLeadListView(B2cLeadListView):
    status = States.NON_QUALIFIED
    model = B2CLead


# >>>><<<<<<<<<<<<<<<<<<<<<>>> LOST B2B AND B2C Leads View <<<<<<<<<<<<


class LostB2bLeadListView(B2bLeadListView):
    status = States.LOST
    model = B2BLead


class LostB2cLeadListView(B2cLeadListView):
    status = States.LOST
    model = B2CLead


class CompletedB2bLeadListView(B2bLeadListView):
    status = States.COMPLETED
    model = B2BLead


class CompletedB2cLeadListView(B2cLeadListView):
    status = States.COMPLETED
    model = B2CLead


class B2BLeadDetailView(BreadcrumbMixin, PermissionRequiredMixin, DetailView):
    permission_required = "leads.view_b2blead"
    template_name = "lead_detail.html"
    queryset = B2BLead.objects.select_related(
        "company", "current_state_user"
    )  # Default model, will be overridden in get_object
    context_object_name = "lead"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead_id = self.kwargs.get("pk")
        context["lead_states"] = self.object.states.select_related(
            "created_by"
        ).order_by("-created_at")
        context["company"] = (
            self.object.company
            if isinstance(self.object, B2BLead)
            else self.object.contact
        )

        return context


class B2CLeadDetailView(B2BLeadDetailView):
    # model = B2CLead
    queryset = B2CLead.objects.select_related("contact", "current_state_user")
    template_name = "b2c_lead_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.object.contact
        return context


class ChangeStateView(View):
    # permission_required = "leads.can_change_state"
    template_name = "snippets/validation_block.html"
    model = B2BLead  # Default model, will be overridden in get_object

    def get(self, request, lead_pk, target_state):
        """Handle GET request to display the confirmation modal"""
        lead = get_object_or_404(self.model, pk=lead_pk)
        print("", lead.current_state, target_state)
        target_state_display = States(int(target_state)).label
        print("target_state_display", target_state_display)
        context = {
            "object": lead,
            "target_state": States(int(target_state)),
            "lead_pk": lead_pk,
        }
        return render(request, self.template_name, context)

    def post(self, request, lead_pk, target_state):
        """Handle POST request to actually change the state"""
        lead = get_object_or_404(self.model, pk=lead_pk)
        response = lead.change_state(
            new_state=target_state,
            notes=request.POST.get("notes"),
            user=request.user,
        )
        if response["error"]:
            messages.error(request, response["message"])
        else:
            messages.success(request, "Status mis a jours avec succés")
        return redirect(lead.get_absolute_url())
        # return redirect(reverse("leads:detail_b2blead", kwargs={"pk": lead_pk}) if isinstance(lead, B2BLead) else reverse("leads:detail_b2clead", kwargs={"pk": lead_pk}))


class ChangeB2CStateView(ChangeStateView):
    permission_required = "leads.can_change_b2c_state"
    model = B2CLead  # Override to use B2CLead model
