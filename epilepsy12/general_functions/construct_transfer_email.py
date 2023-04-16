from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


def construct_transfer_epilepsy12_site_email(request, user, target_organisation, child):
    email_template_name = "registration/transer_epilepsy12_site_email.html"
    c = {
        "email": user.email,
        'domain': get_current_site(request),
        'site_name': 'Epilepsy12',
        "user": user,
        'protocol': 'http',
        "target_organisation": target_organisation,
        "child": child,
    }
    email = render_to_string(email_template_name, c)

    return email
