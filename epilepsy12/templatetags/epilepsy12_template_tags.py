from django import template
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
