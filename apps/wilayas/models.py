from django.db import models


class Wilaya(models.Model):
    name = models.CharField(max_length=100)
    ar_name = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    code = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code", "name"]

    @property
    def matricule(self):
        return str(self.mat).zfill(2) or "-"

    def __str__(self):
        return self.name


class Commune(models.Model):

    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ar_name = models.CharField(
        max_length=255, blank=True, null=True
    )  # أضف هذا إن لم يكن موجودًا
    postal_code = models.CharField(max_length=10, blank=True, null=True)  # وأيضًا هذا
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
