from django.db import models
from django.urls import reverse

# Create your models here.


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CRUDUrlMixin:
    @classmethod
    def get_create_url(cls):
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    @classmethod
    def get_list_url(cls):
        return reverse(f"{cls._meta.app_label}:list_{cls._meta.model_name}")

    def get_update_url(self):
        return reverse(
            f"{self._meta.app_label}:update_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )

    def get_delete_url(self):
        return reverse(
            f"{self._meta.app_label}:delete_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )


class Tax(CRUDUrlMixin, TimestampedModel):
    name = models.CharField(max_length=100)
    tax = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taxe"
        verbose_name_plural = "Taxes"
        ordering = ["-created_at"]


class LeadSource(CRUDUrlMixin, TimestampedModel):
    name = models.CharField(max_length=50, verbose_name="Nom")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Source de contact"
        verbose_name_plural = "Sources de contact"


class Potential(CRUDUrlMixin, TimestampedModel):
    segment = models.CharField(
        max_length=1, unique=True, help_text="Lettre de segmentation (A, B, C..etc)"
    )
    min_employees = models.PositiveIntegerField(
        help_text="Seuil d’employés minimum inclusif"
    )
    max_employees = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Seuil d’employés maximum inclusif (laisser vide pour ∞)",
    )
    potentiel = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Tax de formation",
        help_text="Tax de formation / CAT théorique",
    )

    def __str__(self):
        return f"{self.segment} ({self.min_employees} - {self.max_employees if self.max_employees else '∞'} employés) - {self.potentiel} DA"

    def get_absolute_url(self):
        return self.get_update_url()

    class Meta:
        verbose_name = "Potentiel"
        verbose_name_plural = "Potentiels"
        ordering = ["-created_at"]
