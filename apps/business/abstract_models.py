from django.db import models
from tinymce import models as tinymce_models
from django.utils.translation import gettext_lazy as _


class AbstractInformation(models.Model):
    name_company = models.CharField(verbose_name="Nom de l'entreprise", max_length=100)
    name_company_arabic = models.CharField(
        verbose_name="اسم الشركة", max_length=100, null=True, blank=True
    )
    logo = models.ImageField(
        upload_to="images/logos", verbose_name="Logo", null=True, blank=True
    )
    logo_negatif = models.ImageField(
        upload_to="images/slides", verbose_name="Logo négatif", null=True, blank=True
    )
    favicon = models.ImageField(
        upload_to="images/logos", verbose_name="Favicon", null=True, blank=True
    )
    business_owner = models.CharField(
        verbose_name="nom et prenom", max_length=50, blank=True
    )
    business_owner_arabic = models.CharField(
        verbose_name="الاسم واللقب", max_length=50, blank=True, null=True
    )
    wilaya = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(
        verbose_name=_("Address"), max_length=50, blank=True, null=True
    )
    email = models.EmailField(
        verbose_name=_("e-mail entreprise"), max_length=50, blank=True, null=True
    )
    email2 = models.EmailField(
        verbose_name=_("e-mail 2 entreprise"), max_length=50, blank=True, null=True
    )
    phone = models.CharField(
        verbose_name=_("numéro de téléphone de l'entreprise"),
        max_length=50,
        blank=True,
        null=True,
    )
    phone2 = models.CharField(
        verbose_name=_("numéro de téléphone 2 de l'entreprise"),
        max_length=50,
        null=True,
        blank=True,
    )
    phone3 = models.CharField(
        verbose_name=_("numéro de téléphone 3 de l'entreprise"),
        max_length=50,
        null=True,
        blank=True,
    )
    mini_about = models.CharField(
        max_length=80, verbose_name="Description 1", blank=True, null=True
    )
    about = models.CharField(
        max_length=80, verbose_name="Description 2", blank=True, null=True
    )

    class Meta:
        abstract = True


class AbstractLeagal(models.Model):
    rc_code = models.CharField(
        verbose_name=_("Registre de commerce"), max_length=150, null=True, blank=True
    )
    art_code = models.CharField(
        verbose_name=_("Code d'article"), max_length=150, null=True, blank=True
    )
    nif_code = models.CharField(
        verbose_name=_("Numéro d'identité fiscale"),
        max_length=150,
        null=True,
        blank=True,
    )
    nis_code = models.CharField(
        verbose_name=_("Numéro d'identification statistique"),
        max_length=150,
        null=True,
        blank=True,
    )
    bank_number = models.CharField(
        verbose_name=_("Numéro CCP / RIB"), max_length=50, null=True, blank=True
    )
    bank_info = tinymce_models.HTMLField(
        verbose_name=_("Informations CCP, nom, prénom, adresse"), null=True, blank=True
    )

    class Meta:
        abstract = True
