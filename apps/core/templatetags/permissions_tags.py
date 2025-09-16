from django import template

register = template.Library()


@register.filter
def can_edit(obj, user):
    # Check if the user is authenticated
    if not user.is_authenticated:
        return False

    # Example 2: Check model-level 'change' permission
    perm_codename = f"{obj._meta.app_label}.change_{obj._meta.model_name}"
    return user.has_perm(perm_codename)


@register.filter
def can_delete(obj, user):
    if not user.is_authenticated:
        return False

    # Example 2: Check model-level 'change' permission
    perm_codename = f"{obj._meta.app_label}.delete_{obj._meta.model_name}"
    return user.has_perm(perm_codename)
