from datetime import date, timedelta, datetime
import json
import pandas as pd
from django.db.models import ProtectedError, RestrictedError, Sum
from django.db.models.functions import TruncMonth
from django.views.generic import View, DeleteView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_htmx.http import HttpResponseClientRedirect
from django.utils.text import capfirst
from django.db import router


from apps.core.export import DataExporter


from django.contrib.admin.utils import NestedObjects

from django.contrib.auth.decorators import permission_required

from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


class BreadcrumbMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model or self.get_queryset().model
        try:
            list_url = model.get_list_url() if hasattr(model, "get_list_url") else None
            if list_url:
                context["parent_url"] = list_url
        except NoReverseMatch as e:
            print('NoReverseMatch Exception\n \n \n ', e)
            pass

        detail_page = self.object if hasattr(self, "object") else None
        context["page_title"] = (
            detail_page if detail_page else model._meta.verbose_name_plural
        )
        context["title"] = f"{context['page_title']}"
        if detail_page:
            context["title"] = f"{model._meta.verbose_name} - {context['page_title']}"
            context["parent_page"] = model._meta.verbose_name_plural
        return context


class BaseManageHtmxFormView(FormView):
    template_name = "snippets/_create_form.html"
    form_class = None  # Should be set in subclass
    model = None  # Should be set in subclass
    success_message = ""
    hx_triggers = {}
    parent_url_kwarg = None
    permission_required = None

    def get_formsets(self):
        """
        Override this method in subclasses to define formsets.
        Should return a dictionary with formset configurations.
        Example:
        {
            'phone': ContactPhoneModelFormSet(self.request.POST or None, instance=instance, prefix='phone'),
        }
        """
        return {}

    def get_permission_required(self):
        pk = self.kwargs.get("pk")
        if self.permission_required is not None:
            return (self.permission_required,)
        if hasattr(self.model, "_meta"):
            app_label = self.model._meta.app_label
            model_name = self.model._meta.model_name
            if pk:
                return (f"{app_label}.change_{model_name}",)
            else:
                return (f"{app_label}.add_{model_name}",)
        return ()


    def get_object(self):
        kwargs = self.get_form_kwargs()
        return kwargs["instance"] or None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pk = self.kwargs.get("pk")
        parent_pk = None
        kwargs["instance"] = None
        if pk and self.model:
            instance = self.model.objects.get(pk=pk)
            kwargs["instance"] = instance

        for parent_url in self.parent_url_kwarg:
            if self.kwargs.get(parent_url):
                parent_pk = self.kwargs.get(parent_url)
                # initial = kwargs.get('initial', {})
                kwargs[parent_url] = parent_pk
                # kwargs['initial'] = initial
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")

        # Handle create_url if model defines it
        if (
            self.model
            and hasattr(self.model, "get_create_url")
            and callable(getattr(self.model, "get_create_url"))
        ):
            parent_kwargs = {
                parent_url: self.kwargs[parent_url]
                for parent_url in self.parent_url_kwarg
                if parent_url in self.kwargs
            }

            try:
                context["create_url"] = self.model.get_create_url(**parent_kwargs)
            except TypeError:
                context["create_url"] = self.model.get_create_url()

        # Handle update_url if editing an instance
        if pk and self.model:
            instance = self.model.objects.get(pk=pk)
            context[self.model.__name__.lower()] = instance
            if hasattr(instance, "get_update_url") and callable(instance.get_update_url):
                context["update_url"] = instance.get_update_url()

        context["formsets"] = self.get_formsets()
        context["form_verbose_name"] = (
            self.model._meta.verbose_name if self.form_class else None
        )
        return context


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     pk = self.kwargs.get("pk")
    #     # Use model's classmethod for create_url if available
    #     if (
    #         self.model
    #         and hasattr(self.model, "get_create_url")
    #         and callable(getattr(self.model, "get_create_url"))
    #     ):
    #         if (
    #             self.parent_url_kwarg
    #             and self.kwargs.get(self.parent_url_kwarg) is not None
    #         ):
    #             parent_pk = self.kwargs.get(self.parent_url_kwarg)
    #             print('parent_pk:', parent_pk)
    #             try:
    #                 context["create_url"] = self.model.get_create_url(
    #                     **{self.parent_url_kwarg: parent_pk}
    #                 )
    #             except TypeError:
    #                 context["create_url"] = self.model.get_create_url()
    #         else:
    #             context["create_url"] = self.model.get_create_url()
    #     if pk and self.model:
    #         instance = self.model.objects.get(pk=pk)
    #         context[self.model.__name__.lower()] = instance
    #         # Use model's instance method for update_url if available
    #         if hasattr(instance, "get_update_url") and callable(
    #             getattr(instance, "get_update_url")
    #         ):
    #             context["update_url"] = instance.get_update_url()
    #     context["formsets"] = self.get_formsets()
    #     context["form_verbose_name"] = (
    #         self.model._meta.verbose_name if self.form_class else None
    #     )
    #     return context

    def process_formsets(self, instance=None):
        formsets = self.get_formsets()
        for name, formset in formsets.items():
            if formset.is_valid():
                formset.instance = instance
                formset.save()

    def form_valid(self, form):

        instance = form.save(commit=False)
        has_created_by = hasattr(self.model, "created_by")
        if has_created_by:
            form.instance.created_by = self.request.user
        instance = form.save(commit=True)

        self.process_formsets(instance=instance)
        pk = self.kwargs.get("pk")
        if pk:
            messages.success(
                self.request,
                f"{self.model._meta.model_name} " + _("mis à jour avec succès."),
            )
        else:
            messages.success(
                self.request, f"{self.model._meta.model_name} " + _("créé avec succès.")
            )

        if self.request.POST.get("reload_page"):
            return HttpResponseClientRedirect(self.request.META.get("HTTP_REFERER"))

        if self.request.htmx:
            return HttpResponse(
                status=204, headers={"HX-Trigger": json.dumps(self.hx_triggers)}
            )
        else:
            return HttpResponseClientRedirect(self.request.META.get("HTTP_REFERER"))
            

    def form_invalid(self, form):
        print("\n \n \n Form is invalid:", form.errors)
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class DeleteMixinHTMX(PermissionRequiredMixin, DeleteView):
    template_name = "snippets/htmx_delete_modal.html"
    htmx_additional_event = None
    permission_required = None

    def get_permission_required(self):
        if self.permission_required is not None:
            return (self.permission_required,)
        if hasattr(self.model, "_meta"):
            app_label = self.model._meta.app_label
            model_name = self.model._meta.model_name
            return (f"{app_label}.delete_{model_name}",)
        return ()

    def post(self, request, *args, **kwargs):
        # print('BEFORE  SECONS')
        # import time
        # time.sleep(5)  # Simulate processing time
        # print('AFTER   SECONS SLEEP')
        try:
            self.get_object().delete()
            messages.success(
                self.request,
                f"{self.model._meta.model_name} " + _("supprimé avec succès."),
            )

            if request.htmx:
                headers = {
                    "closeModal": "delete_modal",
                    "refresh_table": None,
                    self.htmx_additional_event: None,
                }
                if self.request.POST.get("reload_page"):
                    headers["redirect_to"] = self.model.get_list_url()
                return HttpResponse(
                    status=200, headers={"HX-Trigger": json.dumps(headers)}
                )

        except (ProtectedError, RestrictedError):
            model_name = self.model._meta.model_name
            message = _(
                f"This {model_name} cannot be deleted because it is used elsewhere."
            )
            messages.error(request, message)
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "closeModal": "delete_modal",
                            "refresh_table": None,
                            self.htmx_additional_event: None,
                        }
                    )
                },
            )

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"object": self.get_object()})


################### delete selected rows on table ####################


def get_deleted_objects(objs):
    """
    Find all objects related to ``objs`` that should also be deleted. ``objs``
    must be a homogeneous iterable of objects (e.g. a QuerySet).

    Return a nested list of strings suitable for display in the
    template with the ``unordered_list`` filter.
    """
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = NestedObjects(using=using, origin=objs)
    collector.collect(objs)
    perms_needed = set()

    def format_callback(obj):
        opts = obj._meta
        no_edit_link = "%s: %s" % (capfirst(opts.verbose_name), obj)
        return no_edit_link

    to_delete = collector.nested(format_callback)
    model_count = {
        model._meta.verbose_name_plural: len(objs)
        for model, objs in collector.model_objs.items()
    }
    protected = [format_callback(obj) for obj in collector.protected]

    return to_delete, model_count, perms_needed, protected


class BulkDeleteMixinHTMX(PermissionRequiredMixin, View):
    permission_required = None
    htmx_additional_event = None
    model = None
    template_name = "popups/select_row_delete_popup.html"

    def get_permission_required(self):
        if self.permission_required is not None:
            return (self.permission_required,)

        if hasattr(self.model, "_meta"):
            app_label = self.model._meta.app_label
            model_name = self.model._meta.model_name
            print("app_label, model_name", app_label, model_name)
            return (f"{app_label}.delete_{model_name}",)
        return ()

    def get_selected_items(self, method="GET"):
        data = self.request.GET if method == "GET" else self.request.POST
        selected_rows = data.getlist("selected_rows")
        selected_items = self.model.objects.filter(id__in=selected_rows)
        return selected_items

    def get_context_data(self, **kwargs):
        context = {}
        context["model_name"] = self.model._meta.model_name if self.model else None
        queryset = self.get_selected_items()
        context["queryset"] = queryset
        (
            to_delete,
            model_count,
            perms_needed,
            protected,
        ) = get_deleted_objects(queryset)

        context["deleted_objects"] = [to_delete]

        context["model_count"] = dict(model_count).items()
        context["perms_lacking"] = perms_needed
        context["protected"] = protected
        print("context['model_name']>>>>>>>>>>", context["model_name"])
        return context

    def get(self, request, *args, **kwargs):
        print(">>>>>>>>>>>>>>>Initial GET request")
        print("\n \n \n self.request.GET:", self.request.GET.copy())
        context = self.get_context_data()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print(">>>>>>>>>>>>>>>>> THIS IS A POST >>><<<<<<<<<<<<<<<<<<<<<")
        queryset = self.get_selected_items(method="POST")
        print("\n \n \n queryset:", queryset.count())
        queryset.model._meta
        if queryset:
            queryset.delete()
            messages.success(request, f"Supprimer avec Succés {len(queryset)} Lead(s).")
            print("Selected items found:", queryset.count())

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "refresh_table": None,
                            "closeModal": "kt_modal",
                            self.htmx_additional_event: None,
                        }
                    )
                },
            )
        else:
            messages.warning(request, _("vous devez sélectionner au moins une ligne"))
            print("No selected items found.")

        return HttpResponse(status=204)


################### import mixins ####################


class ImportDataMixin:
    fields = None
    required_fields = None
    
    def get_import_file(self):
        return self.request.FILES.get("import_file")

    def get_type_of_fields_from_model(self):
        model = self.model
        if hasattr(self, "fields") and self.fields:
            field_names = self.fields
        else:
            # Fallback to all model fields if no fields attribute is defined
            all_fields = model._meta.get_fields()
            field_names = [
                f.name
                for f in all_fields
                if f.editable and (
                    not f.is_relation
                    or f.one_to_one
                    or (f.many_to_one and f.related_model)
                )
            ]

        print("field names---------->>>>>:", field_names)
        field_types = {}
        for field_name in field_names:
            field = model._meta.get_field(field_name)
            field_types[field_name] = field.get_internal_type()
            print(f"Field---->>>>>><: {field_name}, Type: {field_types[field_name]}")
        return field_types

    def get_duplicate_check_fields(self):
        """
        Override this method to define which fields to use for duplicate checking.
        Should return a list of field names.
        Example: ['first_name', 'last_name'] or ['name'] for Company
        """
        raise NotImplementedError(
            "You must define `get_duplicate_check_fields` method in your view."
        )
        
    def get_required_fields(self):
        return self.required_fields or [] 
    
    def get_extra_columns(self):
        return []
    
    def process_field_value(self, field_name, field_type, row_value):
        """Process a field value based on its type."""
        if pd.isna(row_value) or row_value == "":
            return None

        # Handle ForeignKey fields
        if field_type == "ForeignKey":
            # Get the related model from the field
            field = self.model._meta.get_field(field_name)
            related_model = field.related_model

            # Try to find existing instance or create new one
            try:
                # First try to get by name (most common lookup)
                if hasattr(related_model, "name"):
                    instance, created = related_model.objects.get_or_create(
                        name=row_value
                    )
                else:
                    # Fallback to first text field or create with minimal data
                    text_fields = [
                        f
                        for f in related_model._meta.fields
                        if f.get_internal_type() in ["CharField", "TextField"]
                    ]
                    if text_fields:
                        lookup_field = text_fields[0].name
                        instance, created = related_model.objects.get_or_create(
                            **{lookup_field: row_value}
                        )
                    else:
                        # If no suitable field found, skip this value
                        return None
                return instance
            except Exception as e:
                print(f"Error processing foreign key {field_name}: {e}")
                return None

        elif field_type == "DateField":
            try:
                return pd.to_datetime(row_value, errors="coerce").date()
            except Exception as e:
                logger.error(f"Error processing date field {field_name}: {e}")
                return None

        elif field_type == "BooleanField":
            if isinstance(row_value, bool):
                return row_value
            return str(row_value).lower() in ["true", "1", "yes", "on", "oui"]

        elif field_type in ["DecimalField", "FloatField"]:
            try:
                return float(row_value)
            except (ValueError, TypeError):
                return None

        elif field_type in [
            "IntegerField",
            "BigIntegerField",
            "SmallIntegerField",
            "PositiveIntegerField",
        ]:
            try:
                return int(row_value)
            except (ValueError, TypeError):
                return None

        # Default: return the value as-is for text fields
        return row_value

    def process_import_data(self, dbframe):
        field_mappings = self.get_type_of_fields_from_model()
        duplicate_fields = self.get_duplicate_check_fields()
        required_fields = self.get_required_fields()  # New: for checking completeness

        created_count = 0
        updated_count = 0
        skipped_rows = 0
        
        for index, row in dbframe.iterrows():
            instance_data = {}

            # Process each field mapping
            for file_column, field_type in field_mappings.items():
                if file_column in row:
                    field_name = file_column
                    row_value = row[file_column]

                    # Check for custom processing method (e.g., process_company(self, row_value))
                    custom_method_name = f"process_{field_name}"
                    if hasattr(self, custom_method_name):
                        processed_value = getattr(self, custom_method_name)(row_value)
                    else:
                        processed_value = self.process_field_value(
                            field_name, field_type, row_value
                        )

                    if processed_value is not None:
                        instance_data[field_name] = processed_value

            # New: Skip if required fields are missing/null
            missing_required = [
                field for field in required_fields
                if field not in instance_data or instance_data[field] is None
            ]
            if missing_required:
                skipped_rows += 1
                continue  # Or log: print(f"Skipped row {index}: missing {missing_required}")

            # Check for duplicates - Only check fields that have values
            duplicate_filter = {
                field: instance_data[field]
                for field in duplicate_fields
                if field in instance_data and instance_data[field]
            }

            if duplicate_filter:
                existing_instance = self.model.objects.filter(**duplicate_filter).first()
            else:
                existing_instance = None

            try:
                if existing_instance is None:
                    # Changed: Use all instance_data instead of just 'name'
                    instance = self.model.objects.create(**instance_data)
                    created_count += 1
                else:
                    # Update the existing instance with new data
                    for key, value in instance_data.items():
                        setattr(existing_instance, key, value)
                    existing_instance.save()
                    instance = existing_instance
                    updated_count += 1
            except Exception as e:  # Catch errors like IntegrityError
                print(f"Error processing row {index}: {e}")
                skipped_rows += 1
                continue
            
            extra_columns = self.get_extra_columns()
            for extra_col in extra_columns:
                if extra_col in row:
                    row_value = row[extra_col]
                    custom_method_name = f"process_{extra_col}"
                    if hasattr(self, custom_method_name):
                        try:
                            getattr(self, custom_method_name)(instance, row_value, row)
                        except Exception as e:
                            print(f"Error processing extra column '{extra_col}' for row {index}: {e}")
                    else:
                        print(f"Warning: No process method defined for extra column '{extra_col}' in row {index}")
                        
            self.process_multiple_related_fields(instance, row)

        model_name = self.model._meta.verbose_name_plural
        messages.success(self.request, f"{created_count} {model_name} created successfully.")
        if updated_count > 0:
            messages.success(self.request, f"{updated_count} {model_name} updated successfully.")
        if skipped_rows > 0:
            messages.warning(
                self.request,
                f"{skipped_rows} rows skipped (duplicates, missing data, or errors).",
            )

    def process_multiple_related_fields(self, instance, row):
        """ "
        Process all configured related fields dynamically.
        This method should be overridden in subclasses to handle specific related fields.
        """
        pass

    def process_related_field(self, instance, row, config):
        """
        exemple config:
            {
                'model': ContactPhone,
                'foreign_key_field': 'contact',
                'value_field': 'phone',
                'column_prefix': 'phone'
            }
        """
        related_model = config["model"]
        foreign_key_field = config["foreign_key_field"]
        value_field = config["value_field"]
        column_prefix = config["column_prefix"]

        # Find all columns with the specified prefix
        related_columns = [col for col in row.index if col.lower().startswith(column_prefix)]

        for i, col in enumerate(related_columns):
            if pd.notna(row[col]) and str(row[col]).strip() != "":
                value = str(row[col]).strip()
                if value:
                    related_model.objects.get_or_create(
                        **{foreign_key_field: instance, value_field: value}
                    )
                    print(
                        f"Created/Found {related_model.__name__}: {value} for {instance}"
                    )

    def import_data(self, request):
        import_file = self.get_import_file()

        if import_file is None:
            messages.error(request, _("Please upload a file"))
            return redirect(self.get_failure_url())

        # Check file extension
        filename = import_file.name if hasattr(import_file, "name") else ""
        ext = filename.split(".")[-1].lower()
        if ext not in ["csv", "xls", "xlsx"]:
            messages.error(request, _("Unsupported file type. Please upload a CSV or Excel file."))
            return redirect(self.get_failure_url())

        try:
            if ext == "csv":
                dbframe = pd.read_csv(import_file)
            else:
                dbframe = pd.read_excel(import_file)
        except Exception as e:
            messages.error(request, _("Error reading file: ") + str(e))
            return redirect(self.get_failure_url())

        with transaction.atomic():
            try:
                self.process_import_data(dbframe)
            except Exception as e:
                logger.error(f"Error processing import data: {e}")
                messages.error(request, _("Error processing data: Contact Octopus Support"))
                return redirect(self.get_failure_url())
        return redirect(self.get_success_url())

    def get_failure_url(self):
        return self.request.headers.get("referer", "/")

    def get_success_url(self):
        return self.request.headers.get("referer", "/")

    def get_related_instance(self, model, row, field_name):
        instance = None
        field_value = getattr(row, field_name, None)
        if pd.notna(field_value):
            try:
                lookup_field = (
                    "id" if isinstance(field_value, (int, float)) else "name__iexact"
                )
                instance = model.objects.get(**{lookup_field: field_value})
            except ObjectDoesNotExist:
                # Create a new instance if it does not exist
                instance = model.objects.create(name=field_value)
                messages.success(
                    self.request,
                    _(f"{model.__name__} {field_value} created successfully"),
                )
        return instance

    def get(self, request, *_, **__):
        return redirect(reverse(request.path))
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *_, **__):
        return self.import_data(request)


######################### export mixins #########################


class ExportDataMixin:
    export_functions = {
        "excel": "export_to_excel",
        "csv": "export_to_csv",
        "pdf": "export_to_pdf",
    }
    fields = []

    def get_export_data(self):
        exported_data = []
        for obj in self.model.objects.all():
            row = []
            for field_name in self.fields:
                value = getattr(obj, field_name, "")
                # Handle ManyToMany fields
                field_object = None
                try:
                    field_object = obj._meta.get_field(field_name)
                except Exception:
                    pass
                if field_object and field_object.many_to_many:
                    value = ", ".join(
                        [str(item) for item in getattr(obj, field_name).all()]
                    )
                # Convert related objects or non-primitives to string
                elif not isinstance(value, (str, int, float, bool, type(None))):
                    value = str(value)
                row.append(value)
            exported_data.append(tuple(row))
        return exported_data

    def get_export_columns(self):
        # raise NotImplementedError("You must define `get_export_columns` method in your view.")
        return self.fields

    def export_data(self, request):
        extension = request.POST.get("extension")
        export_function = self.export_functions.get(extension)

        if export_function is None:
            messages.error(
                request, "Please select a valid format to export"
            )
            return redirect(self.get_failure_url())

        data = self.get_export_data()
        columns = self.get_export_columns()
        exporter = DataExporter(data, columns)
        messages.success(request, "exported successfully")

        response = getattr(exporter, export_function)(
            file_name=self.get_export_file_name()
        )
        return response

    def get(self, request, *args, **kwargs):
        return redirect(request.path)  # Fixed to redirect to company list

    def post(self, request, *args, **kwargs):
        return self.export_data(request)

    def get_failure_url(self):
        return reverse(
            self.request.path
        )  # Default to home, but you should override this in your view.

    def get_export_file_name(self):
        return f"{self.model._meta.model_name}_export_{date.today()}"  # Default file name, can be overridden in the view.


class ChartMixin(View):
    """Mixin for generating chart data in Django views."""

    model = None  # Define in subclass
    field_to_aggregate = None  # Field to aggregate (e.g., 'amount')
    date_field = "created_at"  # Date field for filtering/aggregation
    group_by_field = None  # Field for non-monthly grouping (e.g., 'source__name')
    aggregate_function = Sum  # Default to Sum, can be Count
    permission = None  # Optional permission
    template_name = "snippets/chart_graph.html"
    chart_id = "chart"  # Unique chart ID
    chart_title = "Chart"  # Chart title
    chart_type = "bar"  # Chart type (e.g., 'bar', 'pie')

    def get_queryset(self):
        """Return the base queryset. Override to customize."""
        if not self.model:
            logger.error("ChartMixin: model must be defined")
            raise ValueError("Model must be defined")
        return self.model.objects.all()

    def filter_by_date_range(self, queryset, start_date, end_date):
        """Apply date range filter to queryset."""
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = (
                    datetime.strptime(end_date, "%Y-%m-%d")
                    + timedelta(days=1)
                    - timedelta(seconds=1)
                )
                return queryset.filter(
                    **{f"{self.date_field}__range": [start_date, end_date]}
                )
            except ValueError:
                logger.error(f"Invalid date format: {start_date}, {end_date}")
                return queryset
        return queryset

    def get_monthly_data(self, queryset):
        """Aggregate data by month for the current year."""
        current_year = timezone.now().year
        all_months = [datetime(current_year, month, 1) for month in range(1, 13)]
        monthly_counts = {month: 0.0 for month in all_months}

        try:
            monthly_data = (
                queryset.annotate(month=TruncMonth(self.date_field))
                .values("month")
                .annotate(total=self.aggregate_function(self.field_to_aggregate))
                .order_by("month")
            )
            for item in monthly_data:
                month_date = item["month"]
                print("month_date>>>>>>:", month_date)
                print("item>>>>>>>:", item["total"])
                if month_date and month_date.year == current_year:
                    monthly_counts[datetime(current_year, month_date.month, 1)] = float(
                        item["total"] or 0
                    )

        except Exception as e:
            logger.error(f"Monthly data aggregation error: {str(e)}")
            raise

        labels = [month.strftime("%B") for month in all_months]
        chart_data = [monthly_counts[month] for month in all_months]
        return labels, chart_data

    def get_grouped_data(self, queryset):
        """Aggregate data by a specific field."""
        if not self.group_by_field:
            logger.error("ChartMixin: group_by_field must be defined")
            raise ValueError("group_by_field must be defined for non-monthly charts")

        try:
            counts = {}
            for item in queryset.values(self.group_by_field).annotate(
                total=self.aggregate_function(self.field_to_aggregate)
            ):
                field_value = item[self.group_by_field] or "Unknown"
                counts[field_value] = item["total"]
            labels = list(counts.keys())
            chart_data = [float(val) for val in counts.values()]
            return labels, chart_data
        except Exception as e:
            logger.error(f"Grouped data aggregation error: {str(e)}")
            raise

    def get_context_data(self, labels, chart_data):
        """Prepare template context."""
        total = sum(chart_data)
        return {
            "chart_labels": labels,
            "chart_data": chart_data,
            "id": self.chart_id,
            "title": self.chart_title,
            "chart_type": self.chart_type,
            "total": total,
            "room_totals": labels,  # For template compatibility
        }

    def get(self, request, *args, **kwargs):
        """Handle GET request and render chart."""
        if self.permission:
            self.get = permission_required(self.permission)(self.get)

        try:
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            queryset = self.get_queryset()
            queryset = self.filter_by_date_range(queryset, start_date, end_date)

            if self.group_by_field:
                labels, chart_data = self.get_grouped_data(queryset)
            else:
                labels, chart_data = self.get_monthly_data(queryset)

            context = self.get_context_data(labels, chart_data)
            return render(request, self.template_name, context)
        except Exception as e:
            logger.error(f"Chart rendering error: {str(e)}")
            raise


############################### mixins table imported fields ###############################


class TableImportFieldsMixin:
    """This mixin is used only to generate the table on the import model"""
    model = None
    fields = None
    extra_fields = None 
    related_fields = {}
    template_name = "tables/_table_import_fields.html"

    def get_list_related_fields(self):
        """
        returns a list of related fields to be displayed in the import
        exemple if field "phone" the list will be : ['phone_1', 'phone_2', '...']
        """
        return [f"{field}_{i}" for field in self.related_fields for i in range(1, 3)]

    def get_type_of_fields_from_model(self):
        """
        Returns a list of fields from the model, including related fields.
        and if the field is required or not.
        if the field is many to many or choice the dictionary will contain the choices
        """
        if self.fields:
            field_names = self.fields
        else:
            all_fields = self.model._meta.get_fields()
            field_names = [
                f.name for f in all_fields if hasattr(f, "get_internal_type")
            ]

        # Build field info list
        field_info = []
        for field_name in field_names:
            try:
                field = self.model._meta.get_field(field_name)

                # Get field choices if available
                choices = []
                if hasattr(field, "choices") and field.choices:
                    choices = [
                        {"value": choice[0], "label": choice[1]}
                        for choice in field.choices
                    ]
                # GET manytomany related fields
                elif hasattr(field, "related_model") and field.many_to_many:
                    related_model = field.related_model
                    choices = [
                        {"value": obj.pk, "label": str(obj)}
                        for obj in related_model.objects.all()
                    ]
                # elif hasattr(field, 'related_model') and field.one_to_one:
                #     related_model = field.related_model
                #     choices = [{'value': obj.pk, 'label': str(obj)} for obj in related_model.objects.all()]
                # elif hasattr(field, 'get_choices'):
                #     choices = [{'value': choice[0], 'label': choice[1]} for choice in field.get_choices()]

                # Determine if field is required
                required = False
                if hasattr(field, "blank"):
                    required = not field.blank and not field.null
                elif hasattr(field, "null"):
                    required = not field.null

                # Get verbose name
                verbose_name = getattr(field, "verbose_name", field_name)

                # Get help text
                help_text = getattr(field, "help_text", "")

                field_info.append(
                    {
                        "name": field.name,
                        "verbose_name": verbose_name,
                        "type": field.get_internal_type(),
                        "required": required,
                        "choices": choices,
                        "help_text": help_text,
                    }
                )

            except Exception:
                # If field doesn't exist in model, skip it or handle as needed
                continue
        if self.extra_fields:
            field_info += self.extra_fields
        else:
            print('SAAEK ZAYDA \n ')

        return field_info

    def get_context_data(self, **kwargs):
        context = {}
        context["import_fields"] = self.get_type_of_fields_from_model()
        context["related_fields"] = self.get_list_related_fields()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class BaseActionView(PermissionRequiredMixin, FormView):
    htmx_additional_event = None
    model = None
    template_name = "snippets/_create_form.html"
    form_class = None
    parent_url_kwarg = None
    action_class_method = None

    def get_parent_object(self):
        if self.parent_url_kwarg:
            return get_object_or_404(
                self.model, pk=self.kwargs.get(self.parent_url_kwarg)
            )
        return None

    def get_selected_items(self, method="GET"):
        data = self.request.GET if method == "GET" else self.request.POST
        selected_rows = data.getlist("selected_rows")
        selected_items = self.model.objects.filter(id__in=selected_rows)
        return selected_items

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {}
        parent = self.get_parent_object()
        if parent:
            kwargs["parent"] = parent
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def get(self, request, *args, **kwargs):
        print(f"DEBUG: GET request received at {request.path}")
        items = self.get_selected_items("GET")
        print(f"DEBUG: Selected items count: {items.count()}")

        if not items.exists():
            print("DEBUG: No items selected")
            messages.warning(request, "Vous devez sélectionner au moins une ligne")
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "closeModal": "kt_modal",
                        }
                    )
                },
            )
        return self.render_to_response(self.get_context_data())

        if not self.form_class:
            print("DEBUG: No form class defined, skipping to form_valid")
            # no form needed → skip straight to success
            return self.form_valid()

        print(f"DEBUG: Form class found: {self.form_class.__name__}")
        form_kwargs = self.get_form_kwargs()
        print(f"DEBUG: Form kwargs: {form_kwargs}")
        form = self.form_class(**form_kwargs)

        context = {
            "form": form,
            "selected_items": items,
        }
        print(
            f"DEBUG: Rendering template {self.template_name} with context keys: {list(context.keys())}"
        )
        return render(request, self.template_name, context)

    def process_action(self):
        raise NotImplementedError(
            "You must define `process_action` method in your view."
        )

    def post(self, request, *args, **kwargs):
        items = self.get_selected_items("POST")
        if not items.exists():
            messages.warning(request, "Vous devez sélectionner au moins une ligne")
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "closeModal": "kt_modal",
                        }
                    )
                },
            )

        result = self.process_action()

        if "errors" in result:
            form = self.form_class(request.POST)
            messages.error(self.request, result["errors"])

            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "selected_items": items,
                },
            )
        else:
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
