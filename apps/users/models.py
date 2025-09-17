# Create your models here.
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.apps import apps
from apps.core.models import CRUDUrlMixin, TimestampedModel
from django.db.models.functions import Concat
from django.db.models import Subquery, OuterRef, Count, Sum, Exists, Q, F, Value


class UserQueryset(models.QuerySet):

    def limit_user(self, user):

        if user.is_superuser:
            return self.all()
        if user.is_staff and user.has_perm("users.view_user"):
            return self.exclude(is_superuser=True)
        if self.filter(supervisor=user).exists():
            return self.filter(supervisor=user)
        return self.filter(id=user.id)

    def include_counts(
        self,
        lead_model=None,
        related_lead_model=None,
        state_model=None,
        start_date=(timezone.now() - timedelta(days=1)).replace(
            hour=18, minute=0, second=0
        ),
        stop_date=timezone.now(),
    ):
        from apps.leads.models import States

        now = timezone.now()

        annotations = {
            "affected_total": Count(
                related_lead_model,
                filter=Q(**{f"{related_lead_model}__current_state_user": F("pk")}),
                distinct=True,
            ),
            # 'completed_total': Count(
            #     related_lead_model,
            #     filter=Q(
            #         **{f"{related_lead_model}__current_state_user": F('pk')},
            #         **{f"{related_lead_model}__current_state": States.COMPLETED},
            #     ),
            #     distinct=True
            # ),
            "not_treated_total": Count(
                related_lead_model,
                filter=Q(
                    **{f"{related_lead_model}__current_state_user": F("pk")},
                    **{f"{related_lead_model}__current_state": States.UNTREATED},
                ),
                distinct=True,
            ),
            
            "affected": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.UNTREATED,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "qualified": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.QUALIFIED,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "not_qualified": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.NON_QUALIFIED,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "injoignable": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.INJOIGNABLE,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "not_interessted": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.NON_INTERESSE,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "lost": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.LOST,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            "completed": Subquery(
                apps.get_model("leads", state_model)
                .objects.filter(
                    created_by=OuterRef("pk"),
                    state=States.COMPLETED,
                    created_at__gte=start_date,
                    created_at__lte=stop_date,
                )
                .values("created_by")
                .annotate(count=Count("lead", distinct=True))
                .values("count")[:1],
                output_field=models.IntegerField(),
            ),
            # 'not_qualified_total': Count(
            #     related_lead_model,
            #     filter=Q(
            #         **{f"{related_lead_model}__current_state_user": F('pk')},
            #         **{f"{related_lead_model}__current_state": States.NOT_QUALIFIED}
            #     ),
            #     distinct=True
            # ),
        }

        # Conditionally add annual_goal for B2BLead only
        if lead_model == "B2BLead":

            annotations["annual_goal"] = Subquery(
                apps.get_model("leads", lead_model)
                .objects.filter(
                    current_state_user=OuterRef("pk"), updated_at__year=now.year
                )
                .values("current_state_user")
                .annotate(total=Sum("company__annual_goal", distinct=True))
                .values("total")[:1],
                output_field=models.DecimalField(max_digits=10, decimal_places=2),
            )

            annotations["annual_realisation"] = Subquery(
                apps.get_model("transactions", "ClientPayment")
                .objects.filter(
                    bill__lead__current_state_user=OuterRef("pk"),
                    updated_at__year=now.year,
                )
                .values("id")
                .annotate(total=Sum("amount", distinct=True))
                .values("total")[:1],
                output_field=models.DecimalField(max_digits=10, decimal_places=2),
            )

            annotations["monthly_goal"] = annotations["annual_goal"] / 12

            annotations["monthly_realisation"] = Subquery(
                apps.get_model("transactions", "ClientPayment")
                .objects.filter(
                    bill__lead__current_state_user=OuterRef("pk"),
                    updated_at__month=now.month,
                )
                .values("id")
                .annotate(total=Sum("amount", distinct=True))
                .values("total")[:1],
                output_field=models.DecimalField(max_digits=10, decimal_places=2),
            )

            annotations["annual_progress"] = (
                (annotations["annual_realisation"] / annotations["annual_goal"]) * 100
                if annotations["annual_goal"]
                else Value(
                    0, output_field=models.DecimalField(max_digits=10, decimal_places=2)
                )
            )

            annotations["monthly_progress"] = (
                (annotations["monthly_realisation"] / (annotations["monthly_goal"]))
                * 100
                if annotations["monthly_goal"]
                else Value(
                    0, output_field=models.DecimalField(max_digits=10, decimal_places=2)
                )
            )

        return self.annotate(**annotations)

    def include_absence_status(self, **kwargs):
        today = timezone.now().date()
        absences_today = Absence.objects.filter(
            user=OuterRef("pk"), date=today, is_absent=True
        )
        return self.annotate(absence_status_today=Exists(absences_today))

    def include_b2b_counts(
        self,
        start_date=(timezone.now() - timedelta(days=1)).replace(
            hour=18, minute=0, second=0
        ),
        stop_date=timezone.now(),
    ):
        return self.include_counts(
            lead_model="B2BLead",
            related_lead_model="b2bleads",
            state_model="B2BLeadState",
            start_date=start_date,
            stop_date=stop_date,
        )

    def include_b2c_counts(
        self,
        start_date=(timezone.now() - timedelta(days=1)).replace(
            hour=18, minute=0, second=0
        ),
        stop_date=timezone.now(),
    ):
        return self.include_counts(
            lead_model="B2CLead",
            related_lead_model="b2cleads",
            state_model="B2CLeadState",
            start_date=start_date,
            stop_date=stop_date,
        )


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return UserQueryset(self.model, using=self._db)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        groups = extra_fields.pop("groups", None)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if groups:
            user.groups.set(groups)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

    # def include_absence_status(self):
    #     return self.get_queryset().include_absence_status()

    def include_absence_status(self):
        today = timezone.now().date()
        absences_today = Absence.objects.filter(
            user=OuterRef("pk"), date=today, is_absent=True
        )
        return self.get_queryset().annotate(absence_status_today=Exists(absences_today))

    def get_assignable_users(self):
        return (
            self.include_absence_status()
            .filter(
                Q(is_active=True)
                & Q(is_commercial=True)
                & Q(absence_status_today=False)
            )
            .distinct()
        )

    def limit_user(self, user):
        return self.get_queryset().limit_user(user)

    def include_b2b_counts(self):
        return self.get_queryset().include_b2b_counts()

    def include_b2c_counts(self):
        return self.get_queryset().include_b2c_counts()


class User(CRUDUrlMixin, AbstractUser, TimestampedModel):
    """first_name last_name email is_staff is_active date_joined"""

    full_name = models.GeneratedField(
        verbose_name=_("Nom et prenom"),
        expression=Concat("first_name", models.Value(" "), "last_name"),
        output_field=models.CharField(max_length=100),
        db_persist=True,
    )

    username = None
    email = models.EmailField(_("E-mail address"), unique=True)
    picture = models.ImageField(upload_to="images/faces", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Numéro de téléphone"), null=True, blank=True)
    address = models.CharField(
        verbose_name=_("Adresse"), max_length=150, null=True, blank=True
    )
    supervisor = models.ForeignKey(
        "self",
        related_name="team_members",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_commercial = models.BooleanField(default=True)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default="fr")

    tags = models.ManyToManyField(
        "tags.Tags",
        verbose_name=_("Tags"),
        related_name="users",
        blank=True,
        help_text=_("Tags associés à l'utilisateur."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["is_commercial", "supervisor", "email"]),
        ]
        
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("users:detail_user", kwargs={"pk": str(self.pk)})

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("users:bulk_delete_users")

    def create_absence(self):
        print("create_absence---------->")
        today = timezone.now().date()
        absence, created = Absence.objects.get_or_create(
            user=self, date=today, defaults={"is_absent": True}
        )
        if not created:
            if not absence.is_absent:
                absence.is_absent = True
                absence.save()
            else:
                raise ValueError("Absence already marked for today.")
        return absence

    def remove_absence(self):
        today = timezone.now().date()
        try:
            absence = Absence.objects.get(user=self, date=today)
            absence.delete()
        except Absence.DoesNotExist:
            raise ValueError("No absence record found for today.")

    @property
    def is_absent_today(self):
        # Use the annotated field if it exists
        if hasattr(self, "absence_status_today"):
            return self.absence_status_today
        else:
            today = timezone.now().date()
            return self.absences.filter(date=today, is_absent=True).exists()

    # def get_annual_goal(self):
    #     """
    #     Returns the annual goal for the user.
    #     This method should be overridden in subclasses if needed.
    #     """
    #     return None


class Absence(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="absences"
    )
    is_absent = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("user", "date")
        verbose_name = "Absence"
        verbose_name_plural = "Absences"

    def __str__(self):
        return f"{self.user.full_name} - {'Absent' if self.is_absent else 'Present'} on {self.date}"
