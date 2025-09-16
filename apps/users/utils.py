from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def get_permissions():
    models = {
        model.__name__: model for model in apps.get_models(include_auto_created=False)
    }
    excluded_model_names = [
        "LogEntry",
        "HistoricalPresenceCoach",
        "HistoricalCoach",
        "HistoricalPersonnel",
        "Maladie",
        "HistoricalPurchaseOrder",
        "BlacklistedToken",
        "Fonctionalite",
        "AssuranceTransaction",
        "Portfolio",
        "Position",
        "WishlistItem",
        "ThemeScreenShot",
        "OutstandingToken",
        "StockCheckItem",
        "PurchaseOrder",
        "HistoricalAbonnementClient",
        "StockTransfer",
        "Notification",
        "StockTransferLineItem",
        "PurchaseOrderLineItem",
        "HistoricalPresence",
        "AtributesValue",
        "CategorySpecs",
        "EmailConfirmation",
        "EmailAddress",
        "Permission",
        "DiscountLine",
        "Theme",
        "Comment",
        "PhotoComment",
        "ContentType",
        "Session",
        "HistoricalClient",
        "Supplier",
        "Materiel",
        "SocialAccount",
        "StockCheck",
        "PaymentMethod",
        "HistoricalRemuneration",
        "Event",
        "HistoricalPaiement",
        "SocialApp",
        "HistoricalAutre",
        "HistoricalRemunerationProf",
        "BasketLine",
        "Site",
        "HistoricalAssuranceTransaction",
        "Assurance",
        "FAQLandingPage",
        "Plan",
        "PlanPrice",
        "Status",
        "TermsLandingPage",
        "Subscription",
        "ClockedSchedule",
        "SubscriptionItem",
        "Domain",
        "Prospect",
        "CrontabSchedule",
        "IntervalSchedule",
        "PeriodicTask",
        "PeriodicTasks",
        "SolarSchedule",
        "Business",
        "Expense",
        "Income",
        "InvoiceItem",
        "QuoteItem",
        "BusinessSocials",
        "CompanyDocument",
        "CompanyEmail",
        "CompanyPhone",
        "ContactEmail",
        "ContactPhone",
        "DocumentFormation",
        "CategoryFormation",
        "B2BLeadState",
        "B2CLeadState",
        "BusinessEmail",
        "BusinessFinancialInfo",
        "BusinessPhone",
        "Configuration",
        "Commune",
        "Wilaya",
    ]

    excluded_content_types = ContentType.objects.filter(
        app_label__in=[model._meta.app_label for model in models.values()],
        model__in=excluded_model_names,
    )
    content_types = ContentType.objects.exclude(
        id__in=excluded_content_types.values_list("id", flat=True)
    )
    permissions = Permission.objects.filter(
        content_type__in=content_types
    ).select_related("content_type")
    # print('permission---------------',permissions)

    permissions_dict = {}
    for permission in permissions:
        model_class = permission.content_type.model_class()
        if model_class:
            model_name = model_class.__name__
            if model_name not in excluded_model_names:
                if model_name not in permissions_dict:
                    permissions_dict[model_name] = []
                permissions_dict[model_name].append(permission)

    return permissions_dict
