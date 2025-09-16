from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import B2BLead, B2BLeadState, B2CLead, B2CLeadState


@receiver(post_save, sender=B2BLead)
@receiver(post_save, sender=B2CLead)
def reference_product_signal(sender, instance, created, **kwargs):
    if created:
        # LeadState = B2BLeadState if isinstance(instance, B2BLead) else B2CLeadState
        instance.dispatch_lead()
        print("Lead created:", instance)
        # LeadState.objects.create(lead=instance, state=1)


@receiver(post_save, sender=B2BLeadState)
@receiver(post_save, sender=B2CLeadState)
def update_lead_state_signal(sender, instance, created, **kwargs):

    # Push to Lead
    # B2BLead
    # B2CLead
    if created:
        Lead = B2BLead if isinstance(instance, B2BLeadState) else B2CLead
        Lead.objects.filter(pk=instance.lead_id).update(
            current_state=instance.state, current_state_user=instance.created_by
        )


def update_lead_on_state_delete(sender, instance, **kwargs):
    """
    After a LeadState is deleted, recompute the latest state and user for the related Lead.
    """
    lead = instance.lead
    # Find the most recent remaining state
    last = lead.states.order_by("-created_at").first()
    if last:
        lead.current_state = last.state
        lead.current_state_user = last.created_by
    else:
        lead.current_state = None
        lead.current_state_user = None
    # Save only the denormalized fields
    lead.save(update_fields=["current_state", "current_state_user"])


post_save.connect(update_lead_on_state_delete, sender=B2BLeadState)
post_save.connect(update_lead_on_state_delete, sender=B2CLeadState)
