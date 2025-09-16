from django.db import models
from django.db.models import Q



class AutreQuerySet(models.QuerySet):
    def search(self, query):
        if query is None or query == "":
            return self.none()
        query = query.split()
        lookup = Q()
        for value in query:
            lookup |= Q(name__icontains=value) | Q(id__icontains=value)
        return self.filter(lookup).distinct()


class AutreManager(models.Manager):
    def get_queryset(self):
        return AutreQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)


class IncomeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_expense=False)


class ExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_expense=True)
