from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


def construct_extension_granted_email(
    request, organisation, audit_period, extension, action
):
    """
    Renders the email sent when an organisation's submission deadline is
    changed by the audit team.

    ``action`` is one of "granted", "closed", "withdrawn" and selects the
    wording in the template.
    """
    email_template_name = "registration/extension_granted_email.html"
    c = {
        "domain": get_current_site(request),
        "site_name": "Epilepsy12",
        "protocol": "http",
        "organisation": organisation,
        "audit_period": audit_period,
        "extension": extension,  # None when action == "withdrawn"
        "action": action,
    }
    email = render_to_string(email_template_name, c)

    return email
