from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    BulkDeleteGroups,
    DeleteUser,
    UserUpdateView,
    UserCreateView,
    UserBulkDeleteView,
    add_edit_group,
    UserDetailView,
    UserListView,
    change_password,
    LoginView,
    logout_view,
    RoleListView,
    UsersPerformanceB2BView,
    UsersPerformanceB2CView,
    GroupDeleteView,
)
from django.urls import reverse_lazy

app_name = "users"

urlpatterns = [
    path("users/", UserListView.as_view(), name="list_user"),
    path(
        "users-performance-b2b/",
        UsersPerformanceB2BView.as_view(),
        name="performance_b2b_user",
    ),
    path(
        "users-performance-b2c/",
        UsersPerformanceB2CView.as_view(),
        name="performance_b2c_user",
    ),
    path("users/detail/<int:pk>", UserDetailView.as_view(), name="detail_user"),
    path("users/create/", UserCreateView.as_view(), name="create_user"),
    path("users/update/<int:pk>/", UserUpdateView.as_view(), name="update_user"),
    # path('users/create/', UserCreateView.as_view(), name="user_create_view"),
    # path('users/update/<int:pk>/', UserUpdateView.as_view(), name="update_user"),
    path("users/delete/<int:pk>/", DeleteUser.as_view(), name="delete_user"),
    path(
        "users/bulk_delete_users/",
        UserBulkDeleteView.as_view(),
        name="bulk_delete_users",
    ),
    path("users/change_password/<int:pk>/", change_password, name="change_password"),
    ###### AUTHENTICATION ##############
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    # path('signup/', SignupView.as_view(), name="signup"),
    # path('signup_success/', SignupsuccessView.as_view(), name="signup_success"),
    ###### ROLES ##############
    path("grouplist/", RoleListView.as_view(), name="grouplist"),
    path("create_group/", add_edit_group, name="create_group"),
    path("update_group/<int:pk>/", add_edit_group, name="update_group"),
    path("roles/delete/<int:pk>/", GroupDeleteView.as_view(), name="delete_group"),
    path("roles/bulk-delete/", BulkDeleteGroups.as_view(), name="bulk_delete_groups"),
    ###### PASSWORD RESET ##############
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_change_form.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
