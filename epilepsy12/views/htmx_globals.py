# python
import csv

# django
from django.apps import apps
from django.shortcuts import render

# e12
from epilepsy12.models import (
    Registration,
    Site,
)


# HTMX generic partials
def registration_active(request, case_id, active_template):
    """
    Call back from GET request in steps partial template
    Triggered also on registration in the audit
    """
    registration = Registration.objects.get(case=case_id)
    audit_progress = registration.audit_progress
    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    # enable the steps if has just registered
    if audit_progress.registration_complete:
        if active_template == "none":
            active_template = "register"

    context = {
        "audit_progress": audit_progress,
        "active_template": active_template,
        "case_id": case_id,
        "organisation_id": organisation_id,
    }

    return render(
        request=request, template_name="epilepsy12/steps.html", context=context
    )
