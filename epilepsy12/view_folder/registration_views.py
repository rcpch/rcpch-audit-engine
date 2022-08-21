from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
from django_htmx.http import trigger_client_event

from epilepsy12.models.hospital_trust import HospitalTrust
from epilepsy12.view_folder.investigation_views import investigations

from ..models import Registration, Site
from ..models import Case, AuditProgress


@login_required
def register(request, case_id):

    case = Case.objects.get(pk=case_id)
    active_template = "none"

    if not Registration.objects.filter(case=case).exists():
        audit_progress = AuditProgress.objects.create(
            registration_complete=False,
            initial_assessment_complete=False,
            assessment_complete=False,
            epilepsy_context_complete=False,
            multiaxial_description_complete=False,
            management_complete=False,
            investigation_complete=False
        )
        Registration.objects.create(
            case=case,
            audit_progress=audit_progress
        )

    registration = Registration.objects.filter(case=case).get()
    if registration.eligibility_criteria_met and registration.registration_date is not None:
        active_template = "register"

    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    previously_registered = 0

    lead_site = None

    registered_sites = Site.objects.filter(registration=registration)
    for registered_site in registered_sites:
        if registered_site.site_is_primary_centre_of_epilepsy_care and registered_site.site_is_actively_involved_in_epilepsy_care:
            lead_site = registered_site
        elif not registered_site.site_is_actively_involved_in_epilepsy_care:
            previously_registered += 1

    previously_registered_sites = None
    if previously_registered > 0:
        previously_registered_sites = Site.objects.filter(
            registration=registration, site_is_actively_involved_in_epilepsy_care=False, site_is_primary_centre_of_epilepsy_care=True).all()

    context = {
        "registration": registration,
        "case_id": case_id,
        "hospital_list": hospital_list,
        "site": lead_site,
        "previously_registered_sites": previously_registered_sites,
        "initial_assessment_complete": registration.audit_progress.initial_assessment_complete,
        "assessment_complete": registration.audit_progress.assessment_complete,
        "epilepsy_context_complete": registration.audit_progress.epilepsy_context_complete,
        "multiaxial_description_complete": registration.audit_progress.multiaxial_description_complete,
        "investigation_complete": registration.audit_progress.investigation_complete,
        "management_complete": registration.audit_progress.management_complete,
        "active_template": active_template
    }

    response = render(
        request=request, template_name='epilepsy12/register.html', context=context)

    return response


# HTMX endpoints

"""
Lead site allocation, deletion, updating and transfer
"""


def allocate_lead_site(request, registration_id):
    """
    Allocate site when none have been assigned
    """
    registration = Registration.objects.get(pk=registration_id)
    new_trust_id = request.POST.get('allocate_lead_site')
    selected_hospital_trust = HospitalTrust.objects.get(pk=new_trust_id)

    # test if site exists
    if Site.objects.filter(
        registration=registration,
        hospital_trust=selected_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this site already plays an active role in the care of this child
        # update the status therefore to include the lead role

        Site.objects.filter(
            registration=registration,
            hospital_trust=selected_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True
        ).update(
            site_is_primary_centre_of_epilepsy_care=True
        )
    else:
        # this site may still be associated with this registration but not actively
        # it is therefore safe to create a new record
        Site.objects.create(
            registration=registration,
            hospital_trust=selected_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_childrens_epilepsy_surgery_centre=False,
            site_is_paediatric_neurology_centre=False,
            site_is_general_paediatric_centre=True
        )

    # retrieve the current active site
    site = Site.objects.filter(
        registration=registration,
        hospital_trust=selected_hospital_trust,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    ).get()

    # if all registration components present, update AuditProcess
    if registration.eligibility_criteria_met and registration.registration_date:
        # registration now complete
        # TODO need to update this function and the registration_date function to include lead clinician
        registration.audit_progress.registration_complete = True
        registration.save()

    # get the new

    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "hospital_list": hospital_list,
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False
    }

    response = render(
        request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)

    if registration.eligibility_criteria_met:
        # activate registration button if eligibility and lead centre set
        trigger_client_event(
            response=response,
            name="registration_status",
            params={})  # updates the registration status bar with date in the client

    return response


def edit_lead_site(request, registration_id, site_id):
    """
    Edit lead centre button call back from lead_site partial
    Does not edit the centre - returns only the template with the edit set to true
    """
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "hospital_list": hospital_list,
        "registration": registration,
        "site": site,
        "edit": True,
        "transfer": False
    }
    return render(request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)


def transfer_lead_site(request, registration_id, site_id):
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName').all()
    context = {
        "hospital_list": hospital_list,
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": True
    }
    return render(request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)


def cancel_lead_site(request, registration_id, site_id):
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
    context = {
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False,
        'hospital_site': hospital_list
    }
    return render(request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)


def update_lead_site(request, registration_id, site_id, update):
    """
    HTMX POST request on button click from the lead_site partial
    It either edits the existing lead centre or creates a new one and 
    set site_is_actively_involved_in_epilepsy_care and site_is_actively_involved_in_epilepsy_care
    to False in the current record.
    Returns a lead_site partial but also updates the previous_sites partial also
    """

    registration = Registration.objects.get(pk=registration_id)

    if update == "edit":
        new_trust_id = request.POST.get('edit_lead_site')
        new_hospital_trust = HospitalTrust.objects.get(pk=new_trust_id)
        Site.objects.filter(pk=site_id).update(
            hospital_trust=new_hospital_trust,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True)
    elif update == "transfer":
        new_trust_id = request.POST.get('transfer_lead_site')
        new_hospital_trust = HospitalTrust.objects.get(pk=new_trust_id)
        Site.objects.filter(pk=site_id).update(
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=False)
        Site.objects.create(
            hospital_trust=new_hospital_trust,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
            registration=registration)

    site = Site.objects.filter(
        registration=registration,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True).first()

    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False,
        'hospital_list': hospital_list
    }

    response = render(
        request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)

    if registration.eligibility_criteria_met:
        trigger_client_event(
            response=response, name="add_previously_registered_site", params={})

    return response


def delete_lead_site(request, registration_id, site_id):
    """
    HTMX POST request on button click from the lead_site partial
    It deletes the site.
    Returns a lead_site partial but also updates the previous_sites partial also
    """
    registration = Registration.objects.get(pk=registration_id)

    # test first to see if this site is associated with other roles
    # either past or present
    if Site.objects.filter(
        Q(registration=registration) &
        Q(pk=site_id) &
        Q(
            Q(site_is_childrens_epilepsy_surgery_centre=True) |
            Q(site_is_paediatric_neurology_centre=True) |
            Q(site_is_general_paediatric_centre=True)
        )
    ).exists():
        # remove the lead role allocation
        Site.objects.filter(
            pk=site_id
        ).update(site_is_primary_centre_of_epilepsy_care=False)

    else:
        # there are no other roles (previous or current)
        # it is safe to delete this record
        Site.objects.filter(pk=site_id).delete()

    lead_site = Site.objects.filter(
        registration=registration,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True).first()
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
    context = {
        "registration": registration,
        "site": lead_site,
        "edit": False,
        "transfer": False,
        'hospital_list': hospital_list
    }

    response = render(
        request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)
    trigger_client_event(
        response=response, name="add_previously_registered_site", params={})
    return response


@login_required
def previous_sites(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)
    previous_sites = Site.objects.filter(
        registration=registration, site_is_actively_involved_in_epilepsy_care=False, site_is_primary_centre_of_epilepsy_care=True)

    context = {
        'previously_registered_sites': previous_sites,
        'registration': registration
    }
    return render(request=request, template_name="epilepsy12/partials/registration/previous_sites.html", context=context)


"""
Validation process
"""


@login_required
def confirm_eligible(request, registration_id):
    """
    HTMX POST request on button press in registration_form confirming child
    meets eligibility criteria of the audit.
    This will set the eligibility_criteria_met flag in the Registration model
    to True and replace the button with the is_eligible partial, a label confirming
    eligibility. The button will not be shown again.
    """
    context = {
        'has_error': False,
        'message': 'Eligibility Criteria Confirmed.'
    }
    try:
        Registration.objects.update_or_create(pk=registration_id, defaults={
            'eligibility_criteria_met': True
        })
    except Exception as error:
        context = {
            'has_error': True,
            'message': error
        }

    response = render(
        request=request, template_name='epilepsy12/partials/registration/is_eligible_label.html', context=context)

    registration = Registration.objects.filter(pk=registration_id).get()

    if registration.eligibility_criteria_met and Site.objects.filter(registration=registration, site_is_primary_centre_of_epilepsy_care=True).exists():
        # activate registration button if eligibility and lead centre set
        trigger_client_event(
            response=response,
            name="registration_status",
            params={})  # updates the registration status bar with date in the client

    # if all registration components present, update AuditProcess
    if registration.eligibility_criteria_met and registration.registration_date is not None:
        # registration now complete
        AuditProgress.objects.filter(pk=registration.audit_progress.pk).update(
            registration_complete=True
        )
        # TODO need to update this function and the registration_date function to include lead clinician
        # trigger a GET request from the steps template
        trigger_client_event(
            response=response,
            name="registration_active",
            params={})  # reloads the form to show the active steps

    return response


def registration_status(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)
    case = registration.case

    context = {
        'case_id': case.pk,
        'registration': registration
    }

    return render(request=request, template_name='epilepsy12/partials/registration/registration_dates.html', context=context)


@login_required
def registration_date(request, case_id):
    """
    This defines registration in the audit. 
    Call back from POST request on button press of register button
    in registration_dates partial.
    This sets the registration date, and in turn, the cohort number
    It also triggers htmx 'registration_active' to enable the steps
    """
    registration_date = date.today()
    case = Case.objects.get(pk=case_id)

    # update the AuditProgress
    registration = Registration.objects.get(case=case_id)
    registration.registration_date = registration_date
    registration.audit_progress.registration_complete = True

    # update the Registration with the date and the audit_progress record
    registration.save()

    # registration = Registration.objects.filter(case=case).first()

    context = {
        'case_id': case_id,
        'registration': registration
    }

    response = render(
        request=request, template_name='epilepsy12/partials/registration/registration_dates.html', context=context)

    # if all registration components present, update AuditProcess
    registration = Registration.objects.filter(case=case_id).get()
    if registration.eligibility_criteria_met and registration.registration_date is not None:
        # registration now complete
        AuditProgress.objects.filter(pk=registration.audit_progress.pk).update(
            registration_complete=True
        )
        # TODO need to update this function and the registration_date function to include lead clinician
        # trigger a GET request from the steps template
        trigger_client_event(
            response=response,
            name="registration_active",
            params={})  # reloads the form to show the active steps

    return response


def registration_active(request, case_id):
    """
    Call back from GET request in steps partial template
    Triggered also on registration in the audit
    """
    registration = Registration.objects.get(case=case_id)
    audit_progress = registration.audit_progress

    if registration.eligibility_criteria_met:
        active_template = 'register'
    else:
        active_template = 'none'

    context = {
        'initial_assessment_complete': audit_progress.initial_assessment_complete,
        'assessment_complete': audit_progress.assessment_complete,
        'epilepsy_context_complete': audit_progress.epilepsy_context_complete,
        'multiaxial_description_complete': audit_progress.multiaxial_description_complete,
        "investigation_complete": registration.audit_progress.investigation_complete,
        "management_complete": registration.audit_progress.management_complete,
        'active_template': active_template,
        'case_id': case_id
    }

    return render(request=request, template_name='epilepsy12/steps.html', context=context)
