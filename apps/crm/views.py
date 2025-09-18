from django.shortcuts import redirect
from django.views import View
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin
from apps.billing.models import Invoice, Quote
from apps.core.mixins import (
    BaseManageHtmxFormView,
    BreadcrumbMixin,
    BulkDeleteMixinHTMX,
    ChartMixin,
    DeleteMixinHTMX,
    ExportDataMixin,
    ImportDataMixin,
    TableImportFieldsMixin,
)
from apps.crm.filters import CompanyFilterSet, ContactFilterSet
from apps.crm.forms import (
    ActivitySectorModelForm,
    CompanyDocumentModelForm,
    CompanyEmailModelFormSet,
    CompanyFinancialModelForm,
    CompanyModelForm,
    CompanyPhoneModelFormSet,
    ContactEmailModelFormSet,
    ContactModelForm,
    ContactPhoneModelFormSet,
    PublicUrlModelForm,
)
from apps.crm.models.company import (
    ActivitySector,
    Company,
    CompanyDocument,
    CompanyEmail,
    CompanyPhone,
)
from apps.crm.models.contact import Contact, ContactEmail, ContactPhone
from django_filters.views import FilterView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView
from apps.crm.tables import ActivitySectorHtmxTable, CompanyHtmxTable, ContactHtmxTable
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.transactions.models import ClientPayment
from django.db.models import Sum
from django.shortcuts import render
from django.contrib import messages



################### Contacts Views ####################


class ContactListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, ExportMixin, FilterView
):
    permission_required = "crm.view_contact"
    model = Contact
    table_class = ContactHtmxTable
    paginate_by = 20
    filterset_class = ContactFilterSet

    def get_queryset(self):
        queryset = (
            Contact.objects.limit_user(self.request.user)
            .prefetch_related("phones", "emails")
            .select_related("company")
            .order_by("-created_at")
        )
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bulk_delete_url"] = self.model.get_bulk_delete_url()

        context["import_fields_url"] = reverse("crm:import_fields_contact") # we can relace this by a method on the model
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["contact/contact_list.html"]


class CompanyContactsTable(ContactListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get("pk")
        queryset = Contact.objects.filter(company__pk=pk).order_by("-created_at")
        return queryset


class ContactDetailView(BreadcrumbMixin, DetailView):
    model = Contact

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "contact/contact_detail.html"
        return template_name



class CompanyChartView(ChartMixin):
    model = Company
    # field_to_aggregate = 'payments__b2bleads__'
    field_to_aggregate = "leads__bills__payments__amount"
    aggregate_function = Sum
    chart_id = "revenue"
    chart_title = _("Somme des paiements")
    date_field = "leads__bills__payments__created_at"
    chart_type = "line"

    def get_queryset(self):
        """Optimize with select_related."""
        return super().get_queryset().filter(id=self.kwargs.get("pk"))



class ManageContactHTMX(BaseManageHtmxFormView):
    permission_required = "crm.add_contact"
    form_class = ContactModelForm
    model = Contact
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }
    parent_url_kwarg = ("company_pk",)

    def get_formsets(self):
        instance = self.get_object()
        return {
            "phone": ContactPhoneModelFormSet(
                self.request.POST or None, instance=instance, prefix="phone"
            ),
            "email": ContactEmailModelFormSet(
                self.request.POST or None, instance=instance, prefix="email"
            ),
        }

### public form URLs ############
class ManagePublicForm(ManageContactHTMX):
    template_name = "contact/public_forms_url.html"
    form_class = PublicUrlModelForm

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, _("Affiliate registration successful"))
        return redirect('crm:thank_you_view') 

def thank_you_view(request):
    context = {}
    return render(request, 'contact/thank_you.html', context)
####################################################

class DeleteContact(DeleteMixinHTMX):
    permission_required = "crm.delete_contact"
    model = Contact


class DeleteBulkContacts(BulkDeleteMixinHTMX):
    permission_required = "crm.delete_contact"
    model = Contact


class ImportContacts(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "crm.add_contact"
    model = Contact
    fields = [
        "first_name",
        "last_name",
        "company",
        "position",
        "service",
        "address",
        "birth_date",
        "dette",
    ]
    
    related_fields_config = {
        "phone": {
            "model": ContactPhone,
            "foreign_key_field": "contact",
            "value_field": "phone",
            "column_prefix": "phone",
        },
        "email": {
            "model": ContactEmail,
            "foreign_key_field": "contact",
            "value_field": "email",
            "column_prefix": "email",
        },
    }

    def process_multiple_related_fields(self, instance, row):
        """Process all configured related fields dynamically"""
        for field_name, config in self.related_fields_config.items():
            self.process_related_field(instance, row, config)

    def get_duplicate_check_fields(self):
        return ['first_name', 'last_name', 'company']
    
    def get_extra_columns(self):
        return ['create_lead']
    
    def process_create_lead(self, instance, row_value, row):
        should_create = self.process_field_value('dummy', 'BooleanField', row_value)
        if should_create:
            instance.create_lead()
            # Create Lead for this Contact; pull extra data from row if needed (e.g., 'lead_source')
            print(f"Created Lead for Contact: {instance}")


class ImportFieldsContact(TableImportFieldsMixin, View):
    model = Contact
    fields = [
        "first_name",
        "last_name",
        "company",
        "position",
        "service",
        "address",
        "birth_date",
        "dette",
    ]
    related_fields = {
        "phone": {
            "model": ContactPhone,
            "foreign_key_field": "contact",
        },
        "email": {
            "model": ContactEmail,
            "foreign_key_field": "contact",
        },
    }
    extra_fields = [
            {
            "name": "create_lead",
            "verbose_name": "Create Lead",
            "type": "BooleanField",
            "required": False,
            "choices": None,
            "help_text": _("Si oui, une opportunité sera créée pour ce contact."),
        }
    ]


class ExportContacts(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "crm.view_contact"
    model = Contact
    fields = [
        "first_name",
        "last_name",
        "company",
        "position",
        "service",
        "address",
        "birth_date",
        "dette",
        "nationality",
        "notes",
        "source",
        # "created_at"
    ]


#################### Company Views ####################


class CompanyListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "crm.view_company"
    model = Company
    table_class = CompanyHtmxTable
    paginate_by = 10
    filterset_class = CompanyFilterSet

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .limit_user(self.request.user)
            .include_revenue()
            .select_related(
                "wilaya",
            )
            .prefetch_related("contacts", "activity_sectors", "tags")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        context["import_fields_url"] = reverse("crm:import_fields_company")
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["company/company_list.html"]


class ManageCompanyHTMX(BaseManageHtmxFormView):
    form_class = CompanyModelForm
    model = Company

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_formsets(self):
        instance = self.get_object()
        return {
            "phone": CompanyPhoneModelFormSet(
                self.request.POST or None, instance=instance, prefix="phone"
            ),
            "email": CompanyEmailModelFormSet(
                self.request.POST or None, instance=instance, prefix="email"
            ),
        }


class CompanyFinancialInfo(BaseManageHtmxFormView):
    form_class = CompanyFinancialModelForm
    model = Company

    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.pk = self.kwargs.get("pk")
        context["update_url"] = reverse(
            "crm:update_company_financial", kwargs={"pk": self.pk}
        )
        return context


class ManageCompanyDocumentHTMX(BaseManageHtmxFormView):
    permission_required = "crm.add_company"
    form_class = CompanyDocumentModelForm
    model = CompanyDocument
    parent_url_kwarg = ("company_pk",)
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class DeleteCompanyDocument(DeleteMixinHTMX):
    model = CompanyDocument


class DeleteCompany(DeleteMixinHTMX):
    model = Company


class DeleteBulkCompanies(BulkDeleteMixinHTMX):
    model = Company


class ImportCompanies(PermissionRequiredMixin, ImportDataMixin, View):
    permission_required = "crm.add_company"
    model = Company
    fields = [
        "name",
        "business_owner",
        "annual_tax",
        "employees_count",
        "address",
        "wilaya",
        "commune",
        "notes",
        "activity_sectors",
    ]
    related_fields_config = {
        "phone": {
            "model": CompanyPhone,
            "foreign_key_field": "company",
            "value_field": "phone",
            "column_prefix": "phone",
        },
        "email": {
            "model": CompanyEmail,
            "foreign_key_field": "company",
            "value_field": "email",
            "column_prefix": "email",
        },
    }

    def process_multiple_related_fields(self, instance, row):
        for field_name, config in self.related_fields_config.items():
            self.process_related_field(instance, row, config)
            
        if "lead" in row:
            instance.create_lead(lead_name=row.get("lead"))

    def get_duplicate_check_fields(self):
        return []


class ImportFieldsCompanies(TableImportFieldsMixin, View):
    model = Company
    fields = [
        "name",
        "business_owner",
        "annual_tax",
        "activity_sectors",
        "employees_count",
        "address",
        "wilaya",
        "commune",
        "notes",
    ]
    related_fields = {
        "phone": {
            "model": CompanyPhone,
            "foreign_key_field": "company",
        },
        "email": {
            "model": CompanyEmail,
            "foreign_key_field": "company",
        },
    }


class ExportCompanies(PermissionRequiredMixin, ExportDataMixin, View):
    permission_required = "crm.view_company"
    model = Company
    fields = [
        "name",
        "business_owner",
        "annual_tax",
        "website",
        "employees_count",
        "address",
        "wilaya",
        "commune",
        "notes",
    ]


class CompanyDetailView(BreadcrumbMixin, DetailView):
    model = Company
    paginate_by = 10
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_url"] = reverse(
            "crm:update_company_financial", kwargs={"pk": self.object.pk}
        )
        # context["update_document_url"] = reverse("crm:company_document", kwargs={'pk': self.object.pk})
        context["contacts_count"] = self.object.contacts.count()
        context["leads_count"] = self.object.leads.count()
        context["payments_count"] = ClientPayment.objects.filter(
            bill__lead__company=self.object
        ).count()
        context["invoices_count"] = Invoice.objects.filter(
            lead__company=self.object
        ).count()
        context["quotes_count"] = Quote.objects.filter(
            lead__company=self.object
        ).count()
        context["documents_count"] = self.object.documents.count()
        context["documents"] = self.object.documents.all()
        context["size_class"] = "modal-xl "
        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "company/company_detail.html"
        return template_name


######################################### secteur d'activité #########################################


class ManageActivitySectorHTMX(BaseManageHtmxFormView):
    form_class = ActivitySectorModelForm
    model = ActivitySector
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class DeleteActivitySector(DeleteMixinHTMX):
    permission_required = "crm.delete_activitysector"
    model = ActivitySector


class ActivitySectorListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "crm.view_activitysector"
    model = ActivitySector
    table_class = ActivitySectorHtmxTable
    paginate_by = 10

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["configuration/configuration.html"]






