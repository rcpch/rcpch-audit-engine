from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def percent_complete(registration):
    total = 0
    if registration.audit_progress.initial_assessment_complete:
        total += 12
    if registration.audit_progress.epilepsy_context_complete:
        total += 6
    if registration.audit_progress.multiaxial_description_complete:
        total += 6
    if registration.audit_progress.assessment_complete:
        total += 16
    if registration.audit_progress.investigations_complete:
        total += 4
    if registration.audit_progress.management_complete:
        total += 4
    return total


@register.simple_tag
def characters_left(description):
    length = 5000-len(description)
    colour = 'black'
    if (length < 10):
        colour = 'red'
    safe_text = f'<span style="color:{colour}">{length}</span>'
    return mark_safe(safe_text)


@register.simple_tag
def percentage_of_total(numerator, denominator):
    return round(numerator/denominator*100)


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


@register.filter
def is_in(url_name, args):
    """
    receives the request.resolver_match.url_name
    and compares with the template name (can be a list in a string separated by commas),
    returning true if a match is present
    """
    if args is None:
        return None
    arg_list = [arg.strip() for arg in args.split(',')]
    if url_name in arg_list:
        return True
    else:
        return False


@register.filter
def to_class_name(value):
    if value.__class__.__name__ == "Registration":
        return 'Verification/Registration'
    elif value.__class__.__name__ == "InitialAssessment":
        return 'Initial Assessment'
    elif value.__class__.__name__ == "EpilepsyContext":
        return 'Epilepsy Context'
    elif value.__class__.__name__ == "DESSCRIBE":
        return 'Multiaxial Description'
    elif value.__class__.__name__ == "Assessment":
        return 'Milestones'
    elif value.__class__.__name__ == "Investigations":
        return 'Investigations'
    elif value.__class__.__name__ == "Management":
        return 'Management'
    else:
        return 'Error'
