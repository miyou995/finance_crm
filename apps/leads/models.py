from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from apps.core.models import CRUDUrlMixin, TimestampedModel
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class LeadQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("leads.view_lead"):
            # print('user.is_staff and has_perm')

            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            # print('User.objects.filter(supervisor=user).exists()')
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(current_state_user_id=user.id)
                | Q(current_state_user_id__in=user_team_ids)
            )
        elif user.is_commercial:
            # print('user.is_commercial')
            return self.filter(Q(current_state_user_id=user.id))
        else:
            return self.none()


class B2BLeadQueryset(LeadQueryset):
    pass


class B2CLeadQueryset(LeadQueryset):
    pass


class LeadStateQueryset(models.QuerySet):
    def limit_user(self, user):
        if user.is_superuser:
            # print('user.is_superuser')
            return self.all()
        elif user.is_staff and user.has_perm("leads.view_leadstate"):
            # print('user.is_staff and has_perm')

            return self.all()
        elif User.objects.filter(supervisor=user).exists():
            # print('User.objects.filter(supervisor=user).exists()')
            user_team_ids = user.team_members.values_list("id", flat=True)
            return self.filter(
                Q(lead__current_state_user_id=user.id)
                | Q(lead__current_state_user_id__in=user_team_ids)
            )
        elif user.is_commercial:
            # print('user.is_commercial')
            return self.filter(Q(lead__current_state_user_id=user.id))
        else:
            return self.none()


class States(models.IntegerChoices):

    NEW = 1, _("Nouveau")
    UNTREATED = 2, _("Non traité")
    NON_QUALIFIED = 3, _("Non qualifié")
    QUALIFIED = 4, _("Qualifié")
    INJOIGNABLE = 5, _("Injoignable")
    NON_INTERESSE = 6, _("Non intéressé")
    DUPLICATED = 7, _("Client dupliqué")
    LOST = 8, _("Perdue")
    COMPLETED = 9, _("Gagnée")


class Lead(CRUDUrlMixin, TimestampedModel):
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    source = models.CharField(_("Source"), max_length=100, blank=True, null=True)

    current_state = models.PositiveSmallIntegerField(
        null=True, blank=True, db_index=True, help_text="Latest state from LeadState"
    )

    # assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='leads')
    current_state_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        # related_name="leads",
        related_name="%(class)ss",
        help_text="User who set the latest state",
    )

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = _("Opportunité")
        verbose_name_plural = _("Opportunités")
        ordering = ["-created_at"]

    @classmethod
    def get_create_url(self, company_pk=None):
        if company_pk:
            return reverse(
                f"{self._meta.app_label}:create_company_b2blead",
                kwargs={"company_pk": company_pk},
            )
        return reverse(f"{self._meta.app_label}:create_{self._meta.model_name.lower()}")

    def get_absolute_url(self):
        return reverse(
            f"leads:detail_{self._meta.model_name.lower()}", kwargs={"pk": self.pk}
        )

    def get_change_state_url(self, target_state):
        return reverse(
            f"leads:change_{self._meta.model_name.lower()}_state",
            kwargs={"lead_pk": self.pk, "target_state": target_state},
        )

    def change_state(self, new_state, notes=None, user=None):
        message = {"error": None, "success": None, "message": None}

        # current_state = self.current_state
        # print('states<<<>>>', States.choices)
        # # print('States(current_state)', States(current_state))
        # print('States(new_state)', States(new_state))
        # allowed_states = States.choices
        # if new_state not in allowed_states:
        #     if current_state is None:
        #         message["error"] = "Le statut actuel est inconnu."
        #         return message
        #     current_state_display = States(current_state)
        #     new_state_display = States(new_state)
        #     message["error"] = f"changmeent de status non permit de '{current_state_display}' a '{new_state_display}'."
        # else:

        self.states.model.objects.create(
            lead=self,
            state=new_state,
            notes=notes,
            created_by=user or self.current_state_user,
        )
        message["success"] = "Status changé avec succès."
        return message

    @classmethod  # NOT USED
    def dispatch_leads(cls, number_per_user, users=None):
        if users:
            assignable_users = users
        else:
            assignable_users = User.objects.get_assignable_users()
            if not assignable_users.exists():
                print("Aucun utilisateur disponible pour l'affectation.\n")
                return 0, "Aucun utilisateur disponible pour l'affectation."

        user_list = list(assignable_users)
        user_count = len(user_list)

        total_leads_needed = number_per_user * user_count
        print(f"number_per_user: {number_per_user}\n")
        print(f"total_leads_needed: {total_leads_needed}\n")
        print(f"users: {len(user_list)}\n")

        # Get unassigned leads (latest state is 1)
        unassigned_leads = cls.objects.not_affected_leads().exclude(is_blacklisted=True)
        total_unassigned = unassigned_leads.count()
        print(f"total_unassigned: {total_unassigned}\n")

        if total_unassigned == 0:
            print("Aucun prospect non affecté disponible.\n")
            return 0, "Aucun prospect non affecté disponible."

        # Adjust total leads to assign if not enough unassigned leads are available
        total_leads_to_assign = min(total_leads_needed, total_unassigned)
        leads_to_assign = unassigned_leads[:total_leads_to_assign]
        print(f"total_leads_to_assign: {total_leads_to_assign}\n")
        print(f"leads_to_assign length: {len(leads_to_assign)}\n")

        assigned_count = 0
        lead_index = 0

        with transaction.atomic():
            for user in user_list:
                user_pending_leads = (
                    cls.objects.filter(current_state_user__id=user.id)
                    .non_traite_leads()
                    .count()
                )
                print(f"user_pending_leads: {user_pending_leads}\n")
                needed_leads = number_per_user - user_pending_leads
                if needed_leads <= 0:
                    print(f"User {user} has enough leads.\n")
                    continue

                leads_for_user = leads_to_assign[lead_index : lead_index + needed_leads]
                print(f"Assigning {len(leads_for_user)} leads to user {user}\n")
                for lead in leads_for_user:
                    try:
                        # Change lead state to 'non traité' (state = 2) and assign user
                        lead.change_state(new_state=2, user=user)
                        # print(f'Lead {lead.id} assigned to user {user.id}\n')
                        assigned_count += 1
                    except Exception as e:
                        print(f"There is an error on lead {lead.id}: {e}\n")
                        continue
                lead_index += needed_leads
                print("lead_index>>>>>>>", lead_index)
                if lead_index >= total_leads_to_assign:
                    print(
                        "lead_index >= total_leads_to_assign>>>>>>>",
                        lead_index >= total_leads_to_assign,
                    )
                    break  # No more leads to assign

        print(f"Total leads assigned: {assigned_count}\n")
        return assigned_count, None  # No error message

    @classmethod  # NOT USED
    def dispatch_leads_to_users(cls, leads, user=None):
        if user:
            assignable_users = [user]  # Wrap the single user in a list
        else:
            assignable_users = User.objects.get_assignable_users()
            if not assignable_users.exists():
                return 0, "Aucun utilisateur disponible pour l'affectation."

        user = assignable_users[0]  # Get the single user directly
        number_leads = len(leads)
        assigned_count = 0
        with transaction.atomic():
            for lead in leads:
                try:
                    # Change lead state to 'non traité' (state = 2) and assign user
                    lead.change_state(new_state=2, user=user)
                    assigned_count += 1
                except Exception:
                    continue

        return assigned_count, None  # No error message

    def get_current_state(self):
        if self.current_state is not None:
            return States(self.current_state).label
        return _("Unknown State")

    @property
    def get_status_color(self):
        status_colors = {
            States.NEW: "secondary",
            States.UNTREATED: "primary",
            States.NON_QUALIFIED: "info",
            States.QUALIFIED: "success",
            States.INJOIGNABLE: "dark",
            States.NON_INTERESSE: "danger",
            States.DUPLICATED: "warning",
            States.LOST: "danger",
            States.COMPLETED: "success",
        }
        return status_colors.get(self.current_state, None)


class B2BLead(Lead):
    company = models.ForeignKey(
        "crm.company", related_name="leads", on_delete=models.CASCADE
    )
    objects = B2BLeadQueryset.as_manager()

    class Meta:
        verbose_name = _("B2B Opportunité")
        verbose_name_plural = _("B2B Opportunités")
        ordering = ["-created_at"]

    @classmethod
    def get_create_url(self, company_pk=None):
        if company_pk:
            return reverse(
                f"{self._meta.app_label}:create_company_b2blead",
                kwargs={"company_pk": company_pk},
            )
        return reverse(f"{self._meta.app_label}:create_{self._meta.model_name.lower()}")

    def get_absolute_url(self):
        return reverse("leads:detail_b2blead", kwargs={"pk": self.pk})

    @classmethod
    def get_export_url(cls):
        return reverse("leads:export_b2b_lead")

    @classmethod
    def get_import_url(cls):
        return reverse("leads:import_b2b_lead")

    @classmethod
    def get_list_url(cls):
        return reverse(f"{cls._meta.app_label}:list_lead")

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("leads:bulk_delete_b2b_leads")

    def dispatch_lead(self):
        """
        Determine which user should be assigned the lead based on tag similarity and lead count.
        if a sales man created a company he will be the first assigned user
        the problematic what if after one year the superuser create a new opportunity ( actually the created_by will still get it, is it correct ? # TODO)
        """
        # Convert company tags to a set for efficient intersection

        if self.company.created_by and self.company.created_by.is_active and self.company.created_by.is_commercial:
            self.change_state(new_state=2, user=self.company.created_by)
            self.current_state_user = self.company.created_by
            self.current_state = 2
            self.save(update_fields=["current_state", "current_state_user"])
            return self.company.created_by
        company_tag_ids = set(self.company.tags.values_list("id", flat=True))
        
        # users = User.objects.filter(is_active=True, is_commercial=True).annotate(lead_count=Count('leads'))
        users = (
            User.objects.filter(is_active=True, is_commercial=True)
            .annotate(
                lead_count=Count(
                    "b2bleads",
                    filter=Q(
                        b2bleads__current_state__in=[
                            States.NEW,
                            States.UNTREATED,
                            States.QUALIFIED,
                            States.INJOIGNABLE,
                            States.NON_QUALIFIED,
                        ]
                    ),
                )
            )
            .order_by("-lead_count")
        )

        print("users", users.values("id", "email", "lead_count"))

        candidates = []
        for user in users:
            # Get user tags as a set of tag IDs
            user_tag_ids = set(user.tags.values_list("id", flat=True))
            # Calculate number of common tags
            common_tags = len(user_tag_ids & company_tag_ids)
            candidates.append((user, common_tags, user.lead_count))

        if candidates:
            # Select user with max common tags; if tied, pick the one with fewest leads
            selected_user = max(candidates, key=lambda x: (x[1], -x[2]))[0]
            self.change_state(new_state=2, user=selected_user)
            self.current_state_user = selected_user
            self.current_state = 2
            self.save(update_fields=["current_state", "current_state_user"])
            return selected_user
        else:
            LeadState.objects.create(lead=self, state=1)
        return self


class B2CLead(Lead):
    contact = models.ForeignKey(
        "crm.Contact", related_name="b2c_leads", on_delete=models.CASCADE
    )

    objects = B2CLeadQueryset.as_manager()

    class Meta:
        verbose_name = _("B2C Opportunité")
        verbose_name_plural = _("B2C Opportunités")
        ordering = ["-created_at"]

    @classmethod
    def get_create_url(self, contact_pk=None):
        if contact_pk:
            return reverse(
                f"{self._meta.app_label}:create_contact_b2clead",
                kwargs={"contact_pk": contact_pk},
            )
        return reverse(f"{self._meta.app_label}:create_{self._meta.model_name.lower()}")

    @classmethod
    def get_list_url(cls):
        return reverse(f"{cls._meta.app_label}:list_lead")

    @classmethod
    def get_bulk_delete_url(cls):
        return reverse("leads:bulk_delete_b2c_leads")

    @classmethod
    def get_export_url(cls):
        return reverse("leads:export_b2c_lead")

    @classmethod
    def get_import_url(cls):
        return reverse("leads:import_b2c_lead")

    def dispatch_lead(self):
        """
        Determine which user should be assigned the lead based on tag similarity and lead count.
        """
        # Convert company tags to a set for efficient intersection
        users = (
            User.objects.filter(is_active=True, is_commercial=True)
            .annotate(
                lead_count=Count(
                    "b2bleads",
                    filter=Q(
                        b2bleads__current_state__in=[
                            States.NEW,
                            States.UNTREATED,
                            States.QUALIFIED,
                            States.INJOIGNABLE,
                            States.NON_QUALIFIED,
                        ]
                    ),
                )
            )
            .order_by("-lead_count")
        )
        candidates = []

        # candidates.append((user, user.lead_count))
        print("candidates>>>>>>", candidates)
        if candidates:
            # Select user with max common tags; if tied, pick the one with fewest leads
            selected_user = max(candidates, key=lambda x: (x[1], -x[2]))[0]
            self.change_state(new_state=2, user=selected_user)
            return selected_user
        return None


class LeadState(TimestampedModel):
    state = models.PositiveSmallIntegerField(
        verbose_name=_("Status"), choices=States.choices, default=1
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        # related_name='lead_states',
        related_name="%(class)s_lead_states",
        verbose_name=_("Created by"),
    )
    # lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='%(class)s_states', verbose_name=_("Lead"))
    notes = models.TextField(_("Note"), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            # models.Index(fields=['lead', 'state', 'user', 'created_at']),
            # models.Index(fields=['user', 'state', 'lead']),
            # 2) Today‐range scans per user/state
            models.Index(
                fields=["created_by", "state", "-created_at"],
                name="ls_user_state_created_idx",
            ),
        ]

    def __str__(self):
        return self.get_state_display()

    @property
    def get_state_color(self):
        status_colors = {
            States.NEW: "secondary",
            States.UNTREATED: "primary",
            States.NON_QUALIFIED: "info",
            States.QUALIFIED: "success",
            States.INJOIGNABLE: "dark",
            States.NON_INTERESSE: "danger",
            States.DUPLICATED: "warning",
            States.LOST: "danger",
            States.COMPLETED: "success",
        }
        return status_colors.get(self.state, None)

    def get_current_state(self):
        if self.state is not None:
            label = States(self.state).label
            print("States(self.state).label", label)
            return label
        return _("Unknown State")


class B2BLeadState(LeadState):
    lead = models.ForeignKey(
        B2BLead,
        on_delete=models.CASCADE,
        related_name="states",
        verbose_name=_("B2B Lead"),
    )
    objects = LeadStateQueryset.as_manager()

    class Meta:
        models.Index(fields=["lead", "-created_at"], name="ls_lead_created_idx"),


class B2CLeadState(LeadState):
    lead = models.ForeignKey(
        B2CLead,
        on_delete=models.CASCADE,
        related_name="states",
        verbose_name=_("B2C Lead"),
    )
    objects = LeadStateQueryset.as_manager()

    class Meta:
        models.Index(fields=["lead", "-created_at"], name="ls_lead_created_idx"),
