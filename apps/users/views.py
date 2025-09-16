import json
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic import UpdateView, ListView, TemplateView,DetailView,DeleteView
from django_tables2 import LazyPaginator, SingleTableMixin
from apps.core.mixins import BaseManageHtmxFormView, BreadcrumbMixin, BulkDeleteMixinHTMX, DeleteMixinHTMX
from apps.users.filters import RoleFilterSet, UserB2BPerformanceFilterSet, UserB2CPerformanceFilterSet, UserFilterSet
from apps.users.tables import RoleHTmxTable, UserHTMxTable, UsersPerformanceB2CTable, UsersPerformanceB2BTable
from .models import User
from django.contrib.auth.models import  Permission , Group
from django.contrib.auth.decorators import  permission_required

from django.http import HttpResponse, HttpResponseRedirect
from .forms import (
    AuthenticationForm,
    UserCreationForm,
    ChangePasswordForm,
    AddGroupForm,
    UserUpdateForm,
    UsersActionForm,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
import logging
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext as _
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import login as auth_login
from django.utils import translation
from django.conf import settings
from .utils import get_permissions
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.hashers import check_password
logger = logging.getLogger(__name__)
from django_filters.views import FilterView
from django_tables2.export import ExportMixin

# -----------------------------LOGIN--LOGOUT----------------------------------------------------------


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm

    @method_decorator(login_not_required)
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse("core:index"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if not user:
            messages.error(self.request, _("Email ou mot de passe incorrect."))
            return "/"
        return reverse("users:detail_user", kwargs={"pk": user.pk})

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.error(self.request, _("Email ou mot de passe incorrect."))
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        remember_me = self.request.POST.get("remember_me")
        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)
        user_language = self.request.user.language or "fr"
        translation.activate(user_language)
        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response


def logout_view(request):
    logout(request)
    return redirect("/")


# -----------------------------------USER VIEWS----------------------------------------------------


class ManageUserHTMX(BaseManageHtmxFormView):
    form_class = UserCreationForm
    model = User
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class UserCreateView(ManageUserHTMX):
    form_class = UserCreationForm


class UserUpdateView(ManageUserHTMX):
    """
    we had to create a new class because the form_class is different ( we have to removethe passwords from the form)
    """

    form_class = UserUpdateForm


class UserDetailView(BreadcrumbMixin, DetailView):
    model = User
    context_object_name = "user"
    template_name = "accounts/user-detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context["user_permissions"] = self.object.user_permissions.all()
        context["user_groups"] = self.object.groups.all()
        context["b2b_perfs"] = (
            User.objects.filter(id=self.kwargs.get("pk")).include_b2b_counts().first()
        )
        context["b2c_perfs"] = (
            User.objects.filter(id=self.kwargs.get("pk")).include_b2c_counts().first()
        )

        context["permissions"] = get_permissions()
        # print('permssios ns>>>>>>>>>>', self.get_object().user_permissions.all())
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        perms = request.POST.getlist("perms")
        permissions = Permission.objects.filter(id__in=perms)
        user.user_permissions.set(permissions)
        user.save()
        messages.success(request, _("Profile updated successfully"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class UserListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, ExportMixin, FilterView
):
    permission_required = "users.view_user"
    model = User
    table_class = UserHTMxTable
    paginate_by = 8
    filterset_class = UserFilterSet

    def get_queryset(self):
        queryset = User.objects.limit_user(self.request.user).all()
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["bulk_delete_url"] = self.model.get_bulk_delete_url()
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["accounts/user_list.html"]


class DeleteUser(DeleteMixinHTMX):
    permission_required = "users.delete_user"
    model = User


class UserBulkDeleteView(BulkDeleteMixinHTMX):
    permission_required = "users.delete_user"
    model = User


@permission_required("users.change_user", raise_exception=True)
def change_password(request, pk):
    context = {}
    template_name = "accounts/snippets/change_password.html"
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user_form = ChangePasswordForm(request.POST, instance=user)
        if user_form.is_valid():
            cd = user_form.cleaned_data
            password = cd["password"]
            password2 = cd["password2"]
            if password == password2:
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, _("Mot de passe modifié avec succès"))
                return HttpResponse(
                    status=200,
                    headers={
                        "HX-Trigger": json.dumps(
                            {
                                "closeModal": None,
                                "redirect_to": reverse("users:list_user"),
                            }
                        )
                    },
                )
            else:
                messages.error(request, _("Formulaire invalide"))
        else:
            messages.error(request, _("Formulaire invalide"))
            context["form"] = ChangePasswordForm(data=request.POST or None)
            return render(
                request,
                template_name="accounts/snippets/change_password.html",
                context=context,
            )
    else:
        user_form = ChangePasswordForm()
    context = {"form": user_form, "c_user": user}
    return render(request, template_name, context)



class UsersPerformanceB2BView(BreadcrumbMixin, SingleTableMixin, FilterView):
    permission_required = "users.view_user"
    table_class = UsersPerformanceB2BTable
    filterset_class = UserB2BPerformanceFilterSet
    table_pagination = {
        "per_page": 40,
        "paginator_class": LazyPaginator,
    }
    model = User

    def get_queryset(self):

        qs = (
            User.objects.filter(is_commercial=True)
            .limit_user(self.request.user)
            .include_b2b_counts()
        )
        queryset = self.filterset_class(self.request.GET, queryset=qs).qs
        # print('\n \n \n Queryset:+++++++++++++++++++++++++++++++', queryset.count(  ))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UsersPerformanceB2BView, self).get_context_data(**kwargs)
        context["action_form"] = UsersActionForm()

        context["groups"] = Group.objects.prefetch_related("permissions").all()
        # context["warehouses"] = WareHouse.objects.all()
        # filter_class = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        # context['filter'] = filter_class
        return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "tables/table_partial.html"
        else:
            template_name = "accounts/user_list.html"
        return template_name


class UsersPerformanceB2CView(UsersPerformanceB2BView):
    table_class = UsersPerformanceB2CTable
    filterset_class = UserB2CPerformanceFilterSet

    def get_queryset(self):

        qs = (
            User.objects.filter(is_commercial=True)
            .limit_user(self.request.user)
            .include_b2c_counts()
        )
        queryset = self.filterset_class(self.request.GET, queryset=qs).qs
        return queryset


# -----------------------------------------groupe--------------------------------------------------------

# class ManageGroupHTMX(BaseManageHtmxFormView):
#     permission_required = ('auth.add_group', 'auth.change_group')
#     form_class = AddGroupForm
#     model = Group
#     hx_triggers = {
#         "closeModal": "kt_modal",
#         "refresh_table": None,
#     }

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         return kwargs


#### CREATE  |  #### EDIT

@permission_required(('auth.add_group'), raise_exception=True)

def add_edit_group(request, pk=None):
    context = {}
    context["page_title"] = _("Roles")
    role = None
    if pk:
        role = get_object_or_404(Group.objects.prefetch_related("permissions"), pk=pk)
    form = AddGroupForm(
        instance=role,
    )
    if request.method == "POST":
        form = AddGroupForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            message = _("Role created successfully")
            messages.success(request, str(message))
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "refresh_table": None,
                            "closeModal": "kt_modal",
                        }
                    )
                },
            )
        else:
            messages.error(request, form.errors)
            print("is not valide", form.errors.as_data())

    context["form"] = form
    context["role"] = role
    context["permissions"] = get_permissions()
    return render(request, "accounts/snippets/create_edit_group_form.html", context)


# class RoleListView(PermissionRequiredMixin, ListView):
#     success_url = reverse_lazy('users:grouplist')
#     context_object_name= "roles"

#     def get_context_data(self, **kwargs):
#         context = super(RoleListView, self).get_context_data(**kwargs)
#         context["permissions"] = Permission.objects.all()
#         context["page_title"]= _('Roles')
#         return context


class RoleListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, ExportMixin, FilterView
):
    permission_required = "auth.view_group"
    model = Group
    table_class = RoleHTmxTable
    paginate_by = 8
    filterset_class = RoleFilterSet
    context_object_name = "roles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bulk_delete_url"] =reverse('users:bulk_delete_groups')

        return context

    def get_queryset(self):
        queryset = Group.objects.all()
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["accounts/group_list.html"]


# class RoleDetailView(DetailView):
#     model = Group

#     template_name = "/role/_role_detail.html"
#     def get_context_data(self, **kwargs):
#         context = super(RoleDetailView, self).get_context_data(**kwargs)
#         group = self.object
#         context["staff"] = User.objects.filter(groups__id=group.id)
#         context["page_title"]= _("Role details")
#         context["parent_page"]= _('Users')
#         context["parent_url"]= reverse('users:user_management')
#         return context


class GroupDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "auth.delete_group"
    model = Group
    template_name = "buttons/delete.html"
    success_url = reverse_lazy("users:grouplist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_url"] = reverse(
            "users:delete_group", kwargs={"pk": str(self.object.id)}
        )
        return context


class GroupDeleteView(DeleteMixinHTMX):
    permission_required = "auth.delete_group"
    model = Group


class BulkDeleteGroups(BulkDeleteMixinHTMX):
    permission_required = "auth.delete_group"
    model = Group


# -----------------------------------SignupView---------------------------------------------------------

# class SignupView(FormView):
#     template_name = "accounts/signup.html"
#     form_class = UserCreationForm
#     success_url = reverse_lazy('users:signup_success')
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         form.save()
#         email = form.cleaned_data.get("email")
#         raw_password = form.cleaned_data.get("password1")
#         return response


# class SignupsuccessView(TemplateView):
#     template_name = "accounts/signup_message.html"
