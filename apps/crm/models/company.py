from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.core.models import CRUDUrlMixin, Potential, TimestampedModel
from apps.leads.models import B2BLead
from .base import AbstractEmail, AbstractPhone
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()



def company_document_upload_to(instance, filename):
    return f"company_documents/company_{instance.company.slug}/{filename}"


class CompanyQuerySet(models.QuerySet):

    def limit_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_staff and user.has_perm("crm.view_company"):
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(leads__current_state_user__in=[user.id])
                | Q(leads__current_state_user__in=user_team_ids)
                | Q(leads__isnull=True)
            )
        elif user.is_commercial:
            return self.filter(
                Q(leads__current_state_user__in=[user.id]) | Q(leads__isnull=True)
            )
        else:
            return self.none()

    def include_revenue(self):
        return self.annotate(
            current_year_revenue=models.Sum(
                "leads__invoices__payments__amount",
                filter=models.Q(
                    leads__invoices__payments__created_at__year=timezone.now().year
                ),
            ),
            current_month_revenue=models.Sum(
                "leads__invoices__payments__amount",
                filter=models.Q(
                    leads__invoices__payments__created_at__month=timezone.now().month
                ),
            ),
            last_month_revenue=models.Sum(
                "leads__invoices__payments__amount",
                filter=models.Q(
                    leads__invoices__payments__created_at__month=timezone.now().month
                    - 1
                ),
            ),
        )


class ActivitySector(CRUDUrlMixin, TimestampedModel):
    name = models.CharField(_("Nom du secteur d'activité"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Secteur d'activité")
        verbose_name_plural = _("Secteurs d'activité")
        ordering = ["name"]


class Company(CRUDUrlMixin, TimestampedModel):

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(
        _("Slug"),
        max_length=100,
        unique=True,
        help_text=_("Identifiant unique pour l'entreprise."),
    )

    potentiel = models.ForeignKey(
        "core.Potential",
        verbose_name=_("Potentiel"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    business_owner = models.CharField(
        _("propriétaire d'entreprise"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Nom de la personne responsable de l'entreprise."),
    )
    activity_sectors = models.ManyToManyField(
        ActivitySector, verbose_name=_("Sécteur d'activité"), blank=True
    )
    employees_count = models.PositiveIntegerField(
        verbose_name=_("Nombre d'employés"), default=0
    )
    annual_tax = models.DecimalField(
        _("Tax de formation"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Tax de formation annuel éstimé pour l'entreprise."),
    )
    annual_goal = models.DecimalField(
        _("Objectif Annuel"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Objectif commercial annuel de l'entreprise."),
    )
    website = models.URLField(_("Website"), blank=True, null=True)
    wilaya = models.ForeignKey(
        "wilayas.Wilaya",
        verbose_name=_("Wilaya"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    commune = models.ForeignKey(
        "wilayas.Commune",
        verbose_name=_("Commune"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    tags = models.ManyToManyField(
        "tags.Tags",
        verbose_name=_("Tags"),
        related_name="companies",
        blank=True,
        help_text=_("Tags associés à l'entreprise."),
    )
    # Social media links
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    # Financial information
    capital = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    nif = models.CharField(_("NIF"), max_length=20, blank=True, null=True)
    nrc = models.CharField(_("NRC"), max_length=20, blank=True, null=True)
    nart = models.CharField(_("NART"), max_length=20, blank=True, null=True)
    nis = models.CharField(_("NIS"), max_length=20, blank=True, null=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="created_companies", null=True, blank=True
    )

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = _("Société")
        verbose_name_plural = _("Sociétés")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("crm:detail_company", kwargs={"pk": self.pk})

    @classmethod
    def get_bulk_delete_url(self):
        return reverse("crm:bulk_delete_companies")

    def set_goal(self):
        potential = (
            Potential.objects.filter(
                min_employees__lte=self.employees_count,
            )
            .filter(
                models.Q(max_employees__gte=self.employees_count)
                | models.Q(max_employees__isnull=True)
            )
            .first()
        )
        print("********>>>> potential:", potential)
        if potential:
            print(f"->>>>>>>>>-------------->>>>Setting goal for company: {self.name} with ID: {self.id}")
            self.annual_tax = potential.potentiel
            self.annual_goal = potential.potentiel
            self.potentiel = potential
            # self.save()
            print(
                f"Goal set for company: {self.name} with ID: {self.id} - Goal: {self.annual_goal}"
            )
        else:
            print(f"No potential found for company: {self.name} with ID: {self.id}")
        return self.annual_goal

    @property
    def get_goal(self):
        return int((self.annual_goal * 60) / 100)

    # def get_annual_goal(self):

    def get_potential_color(self):  # NOT used for the moment just to keep it here
        if self.potential == self.Potential.A:
            return "success"
        elif self.potential == self.Potential.B:
            return "warning"
        else:
            return "danger"

    def create_lead(self, lead_name=None):
        """
        Create a lead for the company. we are calling this form the form because we need to check if the create_lead checkbox is checked.
        If the checkbox is checked, we create a lead for the company.
        """
        print("\n \n \n Creating lead for company:", self.name)
        lead = B2BLead.objects.create(
            company=self,
            title=f"{lead_name or self.name}",
        )
        return lead


class CompanyEmail(AbstractEmail):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="emails"
    )
    is_primary = models.BooleanField(_("Primary"), default=False)


class CompanyPhone(AbstractPhone):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="phones"
    )
    is_primary = models.BooleanField(_("Primary"), default=False)


class CompanyDocument(CRUDUrlMixin, TimestampedModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="documents"
    )
    document = models.FileField(_("File"), upload_to=company_document_upload_to)
    description = models.TextField(_("Description"), blank=True, null=True)

    @property
    def filename(self):
        return self.document.name.split("/")[-1]

    @classmethod
    def get_create_url(cls, company_pk=None):
        return reverse("crm:create_companydocument", kwargs={"company_pk": company_pk})

    def __str__(self):
        return f"- {self.filename}"
