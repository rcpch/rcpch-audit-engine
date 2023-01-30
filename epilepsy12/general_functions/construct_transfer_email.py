from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


def construct_transer_epilepsy12_site_email(request, user, target_hospital, child):
    email_template_name = "registration/transer_epilepsy12_site_email.html"
    c = {
        "email": user.email,
        'domain': get_current_site(request),
        'site_name': 'Epilepsy12',
        "user": user,
        'protocol': 'http',
        "target_hospital": target_hospital,
        "child": child,
    }
    email = render_to_string(email_template_name, c)

    return email
