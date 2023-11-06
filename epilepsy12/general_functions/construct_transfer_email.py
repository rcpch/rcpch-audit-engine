from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


def construct_transfer_epilepsy12_site_email(
    request, target_organisation, origin_organisation
):
    email_template_name = "registration/transfer_epilepsy12_site_email.html"
    c = {
        "domain": get_current_site(request),
        "site_name": "Epilepsy12",
        "protocol": "http",
        "target_organisation": target_organisation,
        "origin_organisation": origin_organisation,
    }
    email = render_to_string(email_template_name, c)

    return email


def construct_transfer_epilepsy12_site_outcome_email(
    request, target_organisation, outcome
):
    email_template_name = "registration/transfer_epilepsy12_site_response.html"
    c = {
        "domain": get_current_site(request),
        "site_name": "Epilepsy12",
        "protocol": "http",
        "target_organisation": target_organisation,
        "outcome": outcome,
    }
    email = render_to_string(email_template_name, c)

    return email
