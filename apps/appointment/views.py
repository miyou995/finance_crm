from django_tables2 import SingleTableMixin
from apps.appointment.filters import AppointmentFilterSet
from apps.appointment.forms import AppointmentLeadB2bForm, AppointmentLeadB2cForm
from apps.appointment.models import Appointment
from apps.appointment.tables import AppointmentHtmxTable
from apps.core.mixins import (
    BaseManageHtmxFormView,
    BreadcrumbMixin,
    BulkDeleteMixinHTMX,
    DeleteMixinHTMX,
)
from django.views.generic import ListView
from datetime import date, timedelta
from django_filters.views import FilterView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Case, When, F, CharField, Value
from django.db.models.functions import Concat


class ManageLeadB2bAppointmentHtmx(BaseManageHtmxFormView):
    permission_required = "appointment.add_appointment"
    form_class = AppointmentLeadB2bForm
    model = Appointment
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }
    parent_url_kwarg = "lead_b2b_pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["lead_b2b_pk"] = self.kwargs.get("lead_b2b_pk")
        kwargs["request"] = self.request
        return kwargs


class ManageLeadB2cAppointmentHtmx(ManageLeadB2bAppointmentHtmx):
    form_class = AppointmentLeadB2cForm
    parent_url_kwarg = "lead_b2c_pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["lead_b2c_pk"] = self.kwargs.get("lead_b2c_pk")
        kwargs["request"] = self.request
        return kwargs


class DeleteAppointment(DeleteMixinHTMX):
    permission_required = "appointment.delete_appointment"
    model = Appointment


class DeleteBulkAppointment(BulkDeleteMixinHTMX):
    permission_required = "appointment.delete_appointment"
    model = Appointment


# class AppointmentDetailView(DetailView):
#     model = Appointment
#     template_name = "appointment_detail.html"
#     context_object_name = "appointment"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


class AppointmentCalendarView(ListView):
    model = Appointment
    template_name = "snippets/appointment_calender.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use simple date objects for the template
        days = [date.today() + timedelta(days=i) for i in range(10)]
        appointments = (
            self.model.objects.filter(date__date__in=days)
            .select_related("b2b_lead")
            .prefetch_related("users")
            .order_by("date")
        )
        context["days"] = days
        context["appointments"] = appointments
        return context


class UserAppointmentCalendar(AppointmentCalendarView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pk = self.kwargs.get("pk")
        appointments = (
            self.model.objects.limit_user(self.request.user)
            .filter(date__date__in=context["days"], users__pk=user_pk)
            .select_related("b2b_lead")
            .prefetch_related("users")
            .order_by("date")
        )
        context["appointments"] = appointments
        return context


class AppointmentListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    permission_required = "appointment.view_appointment"
    model = Appointment
    table_class = AppointmentHtmxTable
    filterset_class = AppointmentFilterSet

    def get_queryset(self):
        queryset = (
            Appointment.objects.limit_user(self.request.user)
            .annotate(
                lead_display=Case(
                    When(b2b_lead__isnull=False, then=F("b2b_lead__title")),
                    When(b2c_lead__isnull=False, then=F("b2c_lead__title")),
                    default=Value("No Lead"),
                    output_field=CharField(),
                ),
                name=Case(
                    When(b2b_lead__isnull=False, then=F("b2b_lead__company__name")),
                    When(
                        b2c_lead__isnull=False,
                        then=Concat(
                            F("b2c_lead__contact__first_name"),
                            Value(" "),
                            F("b2c_lead__contact__last_name"),
                        ),
                    ),
                    default=Value("None"),
                    output_field=CharField(),
                ),
            )
            .all()
        )
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bulk_delete_url"] = Appointment.get_bulk_delete_url()
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["appointment_list.html"]
