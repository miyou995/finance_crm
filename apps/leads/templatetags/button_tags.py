from django import template
from django.utils.translation import gettext_lazy as _

from apps.leads.models import States

register = template.Library()

# BUTTON_STATE_MAPPING = {
#     "non_traite_button": 2,
#     "non_qualifie_button": 3,
#     "qualifie_button": 4,
#     "injoignable_button": 5,
#     "non_interesse_button": 6,
#     "deja_appele_button" : 7,
#     "completed_button": 8,  # Assuming this is for completed leads
# }


BUTTONS_MAPPING = {
    # "non_traite_button": {
    #     'state' :
    #     "label": _("Non Traité"),
    #     "icon": "fas fa-circle-info",
    #     "class": "btn-secondary btn-sm",
    # },
    "non_qualifie_button": {
        "state": States.NON_QUALIFIED,
        "label": _("Non Qualifié"),
        "icon": "fas fa-user-times",
        "class": "btn-info ",
    },
    "qualifie_button": {
        "state": States.QUALIFIED,
        "label": _("Qualifié"),
        "icon": "fas fa-user-check",
        "class": "btn-success ",
    },
    "injoignable_button": {
        "state": States.INJOIGNABLE,
        "label": _("Injoignable"),
        "icon": "fas fa-phone-slash",
        "class": "btn-dark",
    },
    "non_interesse_button": {
        "state": States.NON_INTERESSE,
        "label": _("Non Intéressé"),
        "icon": "fas fa-thumbs-down",
        "class": "btn-danger",
    },
    "deja_appele_button": {
        "state": States.DUPLICATED,
        "label": _("Déjà Appelé"),
        "icon": "fa-solid fa-headset",
        "class": "btn-warning ",
    },
    "lost_button": {
        "state": States.LOST,
        "label": _("Perdue"),
        "icon": "fa-solid fa-times",
        "class": "btn-outline btn-outline-dashed btn-outline-danger btn-active-light-danger",
    },
    "completed_button": {
        "state": States.COMPLETED,
        "label": _("Vente Complète"),
        "icon": "fa-solid fa-check",
        "class": "btn-outline btn-outline-dashed btn-outline-success btn-active-light-success",
    },
}
# BUTTON_PERMISSIONS = {
#     "non_traite_button": 'leads.can_change_state',
#     "non_qualifie_button": 'leads.can_change_state',
#     "qualifie_button": 'leads.can_change_state',
#     "injoignable_button": 'leads.can_change_state',
#     "non_interesse_button": 'leads.can_change_state',
#     "deja_appele_button" : 'leads.can_change_state',
#     "completed_button": 'leads.can_change_state',  # Assuming this is for completed leads
# }


@register.inclusion_tag("snippets/leads_buttons_actions.html", takes_context=True)
def render_buttons(context, lead):
    user = context["request"].user
    buttons = {}
    current_state = lead.current_state

    # allowed_states = ALLOWED_TRANSITIONS.get(current_state, [])

    buttons["edit_button"] = user.is_commercial
    buttons["delete_button"] = False
    # buttons["delete_button"] = user.has_perm('leads.delete_lead')

    # Determine which state transition buttons to display
    for button_name, state_number in BUTTONS_MAPPING.items():

        if user.is_commercial:
            # if state_number in allowed_states :
            buttons[button_name] = True
        else:
            buttons[button_name] = False

    # Handle other buttons like 'cancel_button' or 'return_button' if needed
    # For example:
    if current_state and user.has_perm("leads.can_cancel"):
        buttons["cancel_button"] = True
    else:
        buttons["cancel_button"] = False

    return {
        "lead": lead,
        "buttons": buttons,
        "current_state": current_state,
        "action_buttons": BUTTONS_MAPPING,
    }
