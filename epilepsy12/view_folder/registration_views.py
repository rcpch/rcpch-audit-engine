from itertools import count
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
from django_htmx.http import trigger_client_event

from epilepsy12.models.hospital_trust import HospitalTrust

from ..models import Registration, Site
from ..models import Case


@login_required
def register(request, id):

    case = Case.objects.get(pk=id)
    try:
        # create a registration object
        registration, created = Registration.objects.get_or_create(case=case)
    except Exception as error:
        print(f'got or created exception {error}')
        registration = None

    if registration:
        registration_object = registration
        active_template = "unchosen"
    else:
        registration_object = created
        active_template = "none"

    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    # if no allocated site, allocate to organisationname of trust of logged in user
    try:
        user_hospital_trust = HospitalTrust.objects.filter(
            OrganisationName=request.user.hospital_trust).first()

        Site(
            hospital_trust=user_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_childrens_epilepsy_surgery_centre=False,
            site_is_paediatric_neurology_centre=False,
            site_is_general_paediatric_centre=False,
            registration=registration
        ).save()
    except Exception as error:
        print(error)

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
        "registration": registration_object,
        "case_id": id,
        "hospital_list": hospital_list,
        "site": lead_site,
        "previously_registered_sites": previously_registered_sites,
        "initial_assessment_complete": False,
        "assessment_complete": False,
        "epilepsy_context_complete": False,
        "multiaxial_description_complete": False,
        "investigation_management_complete": False,
        "active_template": active_template
    }

    response = render(
        request=request, template_name='epilepsy12/register.html', context=context)

    return response


# HTMX endpoints

@login_required
def registration_date(request, case_id):

    registration_date = date.today()
    case = Case.objects.get(pk=case_id)

    defaults = {
        'registration_date': registration_date,
        'initial_assessment_complete': False,
        'assessment_complete': False,
        'epilepsy_context_complete': False,
        'multiaxial_description_complete': False,
        'investigation_management_complete': False
    }

    Registration.objects.update_or_create(
        defaults=defaults,
        case=case.pk,
    )
    registration = Registration.objects.filter(case=case).first()
    context = {
        'case_id': case_id,
        'registration': registration
    }
    return render(request=request, template_name='epilepsy12/partials/registration/registration_dates.html', context=context)


def allocate_lead_site(request, registration_id):
    """
    Allocate site when none have been assigned
    """
    registration = Registration.objects.get(pk=registration_id)
    new_trust_id = request.POST.get('hospital_trust')

    selected_hospital_trust = HospitalTrust.objects.get(
        OrganisationID=new_trust_id)

    # create a new site
    site = Site.objects.create(
        registration=registration,
        hospital_trust=selected_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_childrens_epilepsy_surgery_centre=False,
        site_is_paediatric_neurology_centre=False,
        site_is_general_paediatric_centre=True
    )
    site.save()

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
    return render(request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)


def edit_lead_site(request, registration_id, site_id):
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
    return render(request=request, template_name="epilepsy12/partials/lead_site.html", context=context)


def transfer_lead_site(request, registration_id, site_id):
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
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
    context = {
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False
    }
    return render(request=request, template_name="epilepsy12/partials/registration/lead_site.html", context=context)


def update_lead_site(request, registration_id, site_id, update):
    new_trust_id = request.POST.get('hospital_trust')
    registration = Registration.objects.get(pk=registration_id)
    new_hospital_trust = HospitalTrust.objects.get(OrganisationID=new_trust_id)

    if update == "edit":
        Site.objects.filter(pk=site_id).update(hospital_trust=new_hospital_trust,
                                               site_is_primary_centre_of_epilepsy_care=True, site_is_actively_involved_in_epilepsy_care=True)
    elif update == "transfer":
        Site.objects.filter(pk=site_id).update(
            site_is_primary_centre_of_epilepsy_care=True, site_is_actively_involved_in_epilepsy_care=False)
        Site.objects.create(hospital_trust=new_hospital_trust,
                            site_is_primary_centre_of_epilepsy_care=True, site_is_actively_involved_in_epilepsy_care=True, registration=registration)

    site = Site.objects.filter(registration=registration, site_is_primary_centre_of_epilepsy_care=True,
                               site_is_actively_involved_in_epilepsy_care=True).first()

    context = {
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False
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


@login_required
def hospital_trust_select(request, registration_id):
    Registration.objects.update_or_create(pk=registration_id, defaults={
        'lead_hospital': request.POST.get('hospital_trust')
    })
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
    context = {
        'hospital_list': hospital_list,
        'selected_lead_hospital': request.POST.get('hospital_trust'),
        'registration_id': registration_id
    }
    return HttpResponse("success")


@login_required
def confirm_eligible(request, registration_id):
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

    trigger_client_event(
        response=response, name="registration_status", params={})

    return response


def registration_status(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)
    case = registration.case

    context = {
        'case_id': case.pk,
        'registration': registration
    }

    return render(request=request, template_name='epilepsy12/partials/registration/registration_dates.html', context=context)
