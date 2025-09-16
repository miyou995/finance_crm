from django.urls import path
from apps.appointment.views import (
    AppointmentListView,
    DeleteAppointment,
    DeleteBulkAppointment,
    ManageLeadB2bAppointmentHtmx,
    AppointmentCalendarView,
    ManageLeadB2cAppointmentHtmx,
    UserAppointmentCalendar,
)

app_name = "appointment"


urlpatterns = [
    path("appointment/list/", AppointmentListView.as_view(), name="list_appointment"),
    path(
        "appointment/appointment_calendar/",
        AppointmentCalendarView.as_view(),
        name="appointment_calendar",
    ),
    ##### user appointment management
    path(
        "appointment/appointment_calendar/user/<int:pk>/",
        UserAppointmentCalendar.as_view(),
        name="user_appointment_calendar",
    ),
    path(
        "appointment/create/leadb2b/<int:lead_b2b_pk>/",
        ManageLeadB2bAppointmentHtmx.as_view(),
        name="create_lead_b2b_appointment",
    ),
    path(
        "appointment/create/leadb2c/<int:lead_b2c_pk>/",
        ManageLeadB2cAppointmentHtmx.as_view(),
        name="create_lead_b2c_appointment",
    ),
    path(
        "appointment/create/",
        ManageLeadB2bAppointmentHtmx.as_view(),
        name="create_appointment",
    ),
    path(
        "appointment/update/<int:pk>/",
        ManageLeadB2bAppointmentHtmx.as_view(),
        name="update_appointment",
    ),
    path(
        "appointment/delete/<int:pk>/",
        DeleteAppointment.as_view(),
        name="delete_appointment",
    ),
    path(
        "appointment/bulk_delete/",
        DeleteBulkAppointment.as_view(),
        name="bulk_delete_appointment",
    ),
    # path('appointment/detail/<int:pk>/', AppointmentDetailView.as_view(), name='detail_appointment'),
]
