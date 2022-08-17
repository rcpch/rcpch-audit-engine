from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def percent_complete(registration):
    total = 0
    if registration.initial_assessment_complete:
        total += 12
    if registration.epilepsy_context_complete:
        total += 6
    if registration.multiaxial_description_complete:
        total += 6
    if registration.assessment_complete:
        total += 16
    if registration.investigation_management_complete:
        total += 12
    return total


@register.simple_tag
def characters_left(description):
    length = 5000-len(description)
    colour = 'black'
    if (length < 10):
        colour = 'red'
    safe_text = f'<span style="color:{colour}">{length}</span>'
    return mark_safe(safe_text)


@register.filter
def custom_filter(text, color):
    safe_text = '<span style="color:{color}">{text}</span>'.format(
        color=color, text=text)
    return mark_safe(safe_text)


@register.simple_tag
def matches_model_field(field_name, model):
    if field_name:
        value = getattr(model, field_name)
        if value:
            return True
        else:
            return False
