from datetime import date
import logging
from django.db import models
from django.db.models.functions import Concat
from django.utils.translation import gettext as _
from django.urls import reverse
from apps.leads.models import B2CLead
from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.crm.models import AbstractEmail, AbstractPhone, Company
from django.contrib.auth import get_user_model
from django.db.models import Q


logger = logging.getLogger(__name__)
User = get_user_model()


class ContactQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("crm.view_contact"):
            # print('user.is_staff and has_perm')
            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            # print('User.objects.filter(supervisor=user).exists()')
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(b2c_leads__current_state_user__in=[user.id])
                | Q(b2c_leads__current_state_user__in=user_team_ids)
                | Q(b2c_leads__isnull=True)
            )
        elif user.is_commercial:
            # print('user.is_commercial')
            return self.filter(
                Q(b2c_leads__current_state_user__in=[user.id])
                | Q(b2c_leads__isnull=True)
            )
        else:
            return self.none()


CIVILITY_CHOICES = (("MLL", "Mlle"), ("MME", "Mme"), ("MR", "Mr"))

BLOOD_CHOICES = (
    ("A-", "A-"),
    ("A+", "A+"),
    ("B-", "B-"),
    ("B+", "B+"),
    ("O-", "O-"),
    ("O+", "O+"),
    ("AB-", "AB-"),
    ("AB+", "AB+"),
)


class Contact(CRUDUrlMixin, TimestampedModel):

    carte = models.CharField(max_length=100, unique=True, blank=True, null=True)
    hex_card = models.CharField(max_length=100, unique=True, blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    full_name = models.GeneratedField(
        verbose_name=_("Nom et prenom"),
        expression=Concat("first_name", models.Value(" "), "last_name"),
        output_field=models.CharField(max_length=100),
        db_persist=True,
    )

    position = models.CharField(
        max_length=255, verbose_name="Poste", blank=True, null=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="contacts",
        verbose_name="Entreprise",
        blank=True,
        null=True,
    )
    service = models.CharField(
        max_length=255, verbose_name="Service", blank=True, null=True
    )
    civility = models.CharField(
        choices=CIVILITY_CHOICES,
        max_length=3,
        default="MME",
        verbose_name="Civilité",
        blank=True,
        null=True,
    )
    picture = models.ImageField(upload_to="contacts/photos", verbose_name="Photo", blank=True, null=True)
    address = models.CharField(
        max_length=200, verbose_name="Adresse", blank=True, null=True
    )
    nationality = models.CharField(
        max_length=50,
        verbose_name="Nationalité",
        default="Algérienne",
        blank=True,
        null=True,
    )
    birth_date = models.DateField(
        max_length=50, verbose_name="Date de naissance", blank=True, null=True
    )
    blood = models.CharField(
        choices=BLOOD_CHOICES, max_length=3, verbose_name="Groupe sanguin"
    )
    notes = models.TextField(blank=True, null=True)
    dette = models.DecimalField(
        max_digits=10, decimal_places=0, blank=True, null=True, default=0
    )
    source = models.ManyToManyField(
        "core.LeadSource", verbose_name="Source de contact", related_name="contacts_sources", blank=True
    )
    
    # interested = models.ManyToManyField( # this is project specific and should be inherited
    #     Group, verbose_name="interesé", related_name="interested", blank=True
    # )
    
    objects = ContactQueryset.as_manager()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ("-created_at",)

    def get_absolute_url(self):
        return reverse("crm:detail_contact", kwargs={"pk": str(self.pk)})

    @classmethod
    def get_create_url(cls, company_pk=None):
        if company_pk:
            return reverse(
                "crm:create_company_contacts", kwargs={"company_pk": company_pk}
            )
        else:
            return reverse("crm:create_contact")

    @property
    def name(self):
        return self.full_name

    @property
    def age(self):
        today = date.today()
        if self.birth_date:
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )
        return None

    def create_lead(self, lead_name=None):
        lead = B2CLead.objects.create(
            contact=self,
            title=f"{lead_name or self.first_name} {self.last_name}",
        )
        print("Lead created---------->>>:", lead)
        return lead

    def get_picture_url(self):
        if self.picture and hasattr(self.picture, "url"):
            return self.picture.url

    @property
    def phone_numbers(self):
        phones = self.phones.all()
        if phones.exists():
            return ", ".join(str(phone) for phone in phones)
        return "-"

    @property
    def emails(self):
        emails = self.emails.all()
        print("emails------------>>>>>>>>", emails)
        if emails.exists():
            return ", ".join(str(email) for email in emails)
        return "-"

    @classmethod
    def get_bulk_delete_url(self):
        return reverse("crm:bulk_delete_contacts")




class ContactEmail(AbstractEmail):
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="emails"
    )
    is_primary = models.BooleanField(_("Primary"), default=False)


class ContactPhone(AbstractPhone):
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="phones"
    )
    is_primary = models.BooleanField(_("Primary"), default=False)
