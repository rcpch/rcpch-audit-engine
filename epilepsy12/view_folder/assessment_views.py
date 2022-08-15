from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from epilepsy12.models.site import Site

from ..models.hospital_trust import HospitalTrust
from ..models import Registration
from ..models import Assessment


@login_required
def consultant_paediatrician_referral_made(request, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    consultant_paediatrician_referral_made = not assessment.consultant_paediatrician_referral_made

    if consultant_paediatrician_referral_made:
        assessment.consultant_paediatrician_referral_made = consultant_paediatrician_referral_made
        assessment.save()
    else:
        assessment.consultant_paediatrician_referral_made = consultant_paediatrician_referral_made
        assessment.consultant_paediatrician_referral_date = None
        assessment.consultant_paediatrician_input_date = None
        assessment.save()

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def consultant_paediatrician_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        consultant_paediatrician_referral_date=datetime.strptime(
            request.POST.get('consultant_paediatrician_referral_date'), "%Y-%m-%d").date())

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)
    sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def consultant_paediatrician_input_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician input date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        consultant_paediatrician_input_date=datetime.strptime(
            request.POST.get('consultant_paediatrician_input_date'), "%Y-%m-%d").date())

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)
    sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)

# centre CRUD


@login_required
def general_paediatric_centre(request, assessment_id):
    """
    HTMX call back from hospital_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to hospital_list partial from
    consultant_paediatrician partial which is its parent
    """
    general_paediatric_centre = HospitalTrust.objects.get(pk=request.POST.get(
        'general_paediatric_centre'))
    assessment = Assessment.objects.get(pk=assessment_id)

    # if centre already has a record in sites associated with this registration,
    # update it include general paediatrics, else create a new record
    site, created = Site.objects.get_or_create(
        registration=assessment.registration,
        hospital_trust=general_paediatric_centre,
        defaults={
            # if this is a new record, need to create all these fields
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_childrens_epilepsy_surgery_centre': False,
            'site_is_actively_involved_in_epilepsy_care': True,
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_paediatric_neurology_centre': False,
            'site_is_general_paediatric_centre': True,
        },
    )
    if not created:
        # this record existed, only the surgical aspects are updated
        Site.objects.update(
            pk=site.pk,
            defaults={
                'site_is_actively_involved_in_epilepsy_care': True,
                'site_is_general_paediatric_centre': True,
            }
        )

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive general paediatric centres
    refreshed_sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in refreshed_sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@ login_required
def edit_general_paediatric_centre(request, assessment_id, site_id):
    """
    HTMX call back from consultant_paediatrician partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """
    new_hospital_trust = HospitalTrust.objects.get(
        pk=request.POST.get('general_paediatric_centre'))

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        registration=assessment.registration,
        hospital_trust=new_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            registration=assessment.registration,
            hospital_trust=new_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        site.site_is_general_paediatric_centre = True
        site.save()
        Site.objects.get(pk=site_id).delete()

    else:
        # this change is a new hospital
        Site.objects.filter(pk=site_id).update(
            hospital_trust=new_hospital_trust,
            site_is_general_paediatric_centre=True,
            site_is_actively_involved_in_epilepsy_care=True
        )

    # refresh sites and return to partial
    sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@ login_required
def update_general_paediatric_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from consultant_paediatrician partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the general_paediatric_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the hospital_list dropdown partial
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    general_paediatric_edit_active = True
    if action == 'cancel':
        general_paediatric_edit_active = False

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": general_paediatric_edit_active
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/general_paediatric.html", context=context)


@ login_required
def delete_general_paediatric_centre(request, assessment_id, site_id):
    """
    HTMX call back from hospitals_select partial template.
    This is a POST request on button click.
    It carries parameters passed in from the consultant_paediatrician partial.
    If the Site object associated with this centre is also associate
    with another centre, the object is updated to reflect not involved in general paediatrics.
    If the Site object is not associated with another centre, it is deleted.
    It returns
    the same partial template.
    """
    error_message = ""

    associated_site = Site.objects.filter(pk=site_id).get()

    if (
        associated_site.site_is_primary_centre_of_epilepsy_care or
        associated_site.site_is_paediatric_neurology_centre or
        associated_site.site_is_childrens_epilepsy_surgery_centre
    ):
        # this site also delivers (or has delivered) surgical or general paediatric care
        # update to remove neurology

        associated_site.site_is_general_paediatric_centre = False
        associated_site.save()

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)
    sites = Site.objects.filter(registration=assessment.registration)

    active_general_paediatric_site = None
    historical_general_paediatric_sites = Site.objects.filter(
        registration=assessment.registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_general_paediatric_site": active_general_paediatric_site,
        "general_paediatric_edit_active": False,
        "error": error_message
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


"""
*** Paediatric neurology ***
"""


@ login_required
def paediatric_neurologist_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, paediatric_neurologist_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                paediatric_neurologist_referral_made=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                paediatric_neurologist_referral_made=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            paediatric_neurologist_referral_made=Q(
                paediatric_neurologist_referral_made=False),
            paediatric_neurologist_referral_date=None,
            paediatric_neurologist_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


@ login_required
def paediatric_neurologist_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        paediatric_neurologist_referral_date=datetime.strptime(
            request.POST.get('paediatric_neurologist_referral_date'), "%Y-%m-%d").date())

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)
    refreshed_sites = Site.objects.filter(registration=assessment.registration)

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in refreshed_sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_neurology_sites": historical_neurology_sites,
        "active_neurology_site": active_neurology_site,
        "neurology_edit_active": False
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


@ login_required
def paediatric_neurologist_input_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        paediatric_neurologist_input_date=datetime.strptime(
            request.POST.get('paediatric_neurologist_input_date'), "%Y-%m-%d").date())

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)
    refreshed_sites = Site.objects.filter(registration=assessment.registration)

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in refreshed_sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_neurology_sites": historical_neurology_sites,
        "active_neurology_site": active_neurology_site,
        "neurology_edit_active": False
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)

# paediatric neurology centre selection


@login_required
def paediatric_neurology_centre(request, assessment_id):
    """
    HTMX call back from hospital_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to hospital_list partial from
    epilepsy_surgery partial which is its parent
    """
    paediatric_neurology_centre = HospitalTrust.objects.get(pk=request.POST.get(
        'paediatric_neurology_centre'))
    assessment = Assessment.objects.get(pk=assessment_id)

    # if centre already has a record in sites associated with this registration,
    # update it include neurology, else create a new record
    site, created = Site.objects.get_or_create(
        registration=assessment.registration,
        hospital_trust=paediatric_neurology_centre,
        defaults={
            # if this is a new record, need to create all these fields
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_childrens_epilepsy_surgery_centre': False,
            'site_is_actively_involved_in_epilepsy_care': True,
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_paediatric_neurology_centre': True,
            'site_is_general_paediatric_centre': False,
        },
    )
    if not created:
        # this record existed, only the surgical aspects are updated
        Site.objects.update(
            pk=site.pk,
            defaults={
                'site_is_actively_involved_in_epilepsy_care': True,
                'site_is_actively_involved_in_epilepsy_care': True,
            }
        )

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres
    refreshed_sites = Site.objects.filter(registration=assessment.registration)

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in refreshed_sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_neurology_sites": historical_neurology_sites,
        "active_neurology_site": active_neurology_site,
        "neurology_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


@ login_required
def edit_paediatric_neurology_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """
    new_hospital_trust = HospitalTrust.objects.get(
        pk=request.POST.get('paediatric_neurology_centre'))

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        registration=assessment.registration,
        hospital_trust=new_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            registration=assessment.registration,
            hospital_trust=new_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        site.site_is_paediatric_neurology_centre = True
        site.save()
        Site.objects.get(pk=site_id).delete()

    else:
        # this change is a new hospital
        Site.objects.filter(pk=site_id).update(
            hospital_trust=new_hospital_trust,
            site_is_paediatric_neurology_centre=True,
            site_is_actively_involved_in_epilepsy_care=True
        )

    # refresh sites and return to partial
    sites = Site.objects.filter(registration=assessment.registration)

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_neurology_sites": historical_neurology_sites,
        "active_neurology_site": active_neurology_site,
        "neurology_edit_active": False
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


@ login_required
def update_paediatric_neurology_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from paediatric_neurology partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the neurology_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the hospital_list dropdown partial
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    neurology_edit_active = True
    if action == 'cancel':
        neurology_edit_active = False

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_neurology_sites": historical_neurology_sites,
        "active_neurology_site": active_neurology_site,
        "neurology_edit_active": neurology_edit_active
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


@ login_required
def delete_paediatric_neurology_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template.
    This is a POST request on button click.
    It carries parameters passed in from the paediatric_neurology partial.
    If the Site object associated with this centre is also associate
    with another centre, the object is updated to reflect not involved in paediatric neurology.
    If the Site object is not associated with another centre, it is deleted.
    It returns
    the same partial template.
    """
    error_message = ""

    associated_site = Site.objects.filter(pk=site_id).get()

    if (
        associated_site.site_is_primary_centre_of_epilepsy_care or
        associated_site.site_is_childrens_epilepsy_surgery_centre or
        associated_site.site_is_general_paediatric_centre
    ):
        # this site also delivers (or has delivered) surgical or general paediatric care
        # update to remove neurology

        associated_site.site_is_paediatric_neurology_centre = False
        associated_site.save()

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)
    sites = Site.objects.filter(registration=assessment.registration)
    # """
    # HTMX callback from the hospitals_select partial, with informaton on which partial it itself is
    # embedded into including site_id and assessment_id

    # """

    active_neurology_site = None
    historical_neurology_sites = Site.objects.filter(
        registration=assessment.registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_surgical_sites": historical_neurology_sites,
        "active_surgical_site": active_neurology_site,
        "surgery_edit_active": False,
        "error": error_message
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurology.html", context=context)


"""
** Children's epilepsy surgery service **
"""


@ login_required
def childrens_epilepsy_surgical_service_referral_criteria_met(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    TODO #69 children's surgery referral criteria
    """

    if Assessment.objects.filter(pk=assessment_id, childrens_epilepsy_surgical_service_referral_criteria_met=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_criteria_met=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_criteria_met=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            childrens_epilepsy_surgical_service_referral_criteria_met=Q(
                childrens_epilepsy_surgical_service_referral_criteria_met=False),
            childrens_epilepsy_surgical_service_referral_made=None,
            childrens_epilepsy_surgical_service_referral_date=None,
            childrens_epilepsy_surgical_service_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def childrens_epilepsy_surgical_service_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, childrens_epilepsy_surgical_service_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_made=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_made=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # A surgical referral has not been made - set all fields related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            childrens_epilepsy_surgical_service_referral_made=Q(
                childrens_epilepsy_surgical_service_referral_made=False),
            childrens_epilepsy_surgical_service_referral_date=None,
            childrens_epilepsy_surgical_service_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration, site_is_childrens_epilepsy_surgery_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        "assessment": assessment,
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": None
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        childrens_epilepsy_surgical_service_referral_date=datetime.strptime(
            request.POST.get('childrens_epilepsy_surgical_service_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration, site_is_childrens_epilepsy_surgery_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        'assessment': assessment,
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": None
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        childrens_epilepsy_surgical_service_input_date=datetime.strptime(
            request.POST.get('childrens_epilepsy_surgical_service_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration, site_is_childrens_epilepsy_surgery_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        'assessment': assessment,
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": None
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)

# children epilepsy surgery centre selection


@ login_required
def epilepsy_surgery_centre(request, assessment_id):
    """
    HTMX call back from hospital_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to hospital_list partial from
    epilepsy_surgery partial which is its parent
    """

    epilepsy_surgery_centre = HospitalTrust.objects.get(pk=request.POST.get(
        'epilepsy_surgery_centre'))
    assessment = Assessment.objects.get(pk=assessment_id)

    # if centre already has record in sites associated with this registration,
    # update it include surgery, else create a new record
    site, created = Site.objects.get_or_create(
        registration=assessment.registration,
        hospital_trust=epilepsy_surgery_centre,
        defaults={
            # if this is a new record, need to create all these fields
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_childrens_epilepsy_surgery_centre': True,
            'site_is_actively_involved_in_epilepsy_care': True,
            'site_is_primary_centre_of_epilepsy_care': False,
            'site_is_paediatric_neurology_centre': False,
            'site_is_general_paediatric_centre': False,
        },
    )
    if site:
        # this record existed, only the surgical aspects are updated
        site.site_is_childrens_epilepsy_surgery_centre = True
        site.site_is_actively_involved_in_epilepsy_care = True
        site.save()

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres
    refreshed_sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration, site_is_childrens_epilepsy_surgery_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in refreshed_sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": None
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def edit_epilepsy_surgery_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template.
    This is a POST request on button click.
    It updates the Site object with the new centre and returns
    the same partial template.
    """
    new_hospital_trust = HospitalTrust.objects.get(
        pk=request.POST.get('epilepsy_surgery_centre'))

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        registration=assessment.registration,
        hospital_trust=new_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            registration=assessment.registration,
            hospital_trust=new_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        site.site_is_childrens_epilepsy_surgery_centre = True
        site.save()
        Site.objects.get(pk=site_id).delete()

    else:
        # this change is a new hospital
        Site.objects.filter(pk=site_id).update(
            hospital_trust=new_hospital_trust,
            site_is_childrens_epilepsy_surgery_centre=True,
            site_is_actively_involved_in_epilepsy_care=True
        )

    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_actively_involved_in_epilepsy_care=False
    ).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": None
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def update_epilepsy_surgery_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from epilepsy_surgery partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the surgery_edit_active flag
    It returns the partial template with the updated flag.
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_actively_involved_in_epilepsy_care=False
    ).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    surgery_edit_active = True
    if action == 'cancel':
        surgery_edit_active = False

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": surgery_edit_active,
        "error": None
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def delete_epilepsy_surgery_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template.
    This is a POST request on button click.
    It carries parameters passed in from the epilepsy_surgery partial.
    If the Site object associated with this centre is also associate
    with another centre, the object is updated to reflect not involved in surgical care.
    If the Site object is not associated with another centre, it is deleted.
    It returns
    the same partial template.
    """
    error_message = ""

    associated_site = Site.objects.filter(pk=site_id).get()

    if (
        associated_site.site_is_primary_centre_of_epilepsy_care or
        associated_site.site_is_paediatric_neurology_centre or
        associated_site.site_is_general_paediatric_centre
    ):
        # this site also delivers (or has delivered) paediatric or general paediatric care
        # update to remove surgery

        associated_site.site_is_childrens_epilepsy_surgery_centre = False
        associated_site.save()

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)
    sites = Site.objects.filter(registration=assessment.registration)

    active_surgical_site = None
    historical_surgical_sites = Site.objects.filter(
        registration=assessment.registration,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_actively_involved_in_epilepsy_care=False
    ).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "historical_surgical_sites": historical_surgical_sites,
        "active_surgical_site": active_surgical_site,
        "surgery_edit_active": False,
        "error": error_message

    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


"""
*** Epilepsy Nurse Specialist ***
"""


@ login_required
def epilepsy_specialist_nurse_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, epilepsy_specialist_nurse_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                individualised_care_plan_in_place=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                individualised_care_plan_in_place=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            epilepsy_specialist_nurse_referral_made=Q(
                epilepsy_specialist_nurse_referral_made=False),
            epilepsy_specialist_nurse_referral_date=None,
            epilepsy_specialist_nurse_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@ login_required
def epilepsy_specialist_nurse_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        epilepsy_specialist_nurse_referral_date=datetime.strptime(
            request.POST.get('epilepsy_specialist_nurse_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@ login_required
def epilepsy_specialist_nurse_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        epilepsy_specialist_nurse_input_date=datetime.strptime(
            request.POST.get('epilepsy_specialist_nurse_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@ login_required
def were_any_of_the_epileptic_seizures_convulsive(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('were_any_of_the_epileptic_seizures_convulsive') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'were_any_of_the_epileptic_seizures_convulsive': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'were_any_of_the_epileptic_seizures_convulsive': False,
            'registration': registration
        })

    if created:
        assessment_object = created
    else:
        assessment_object = assessment

    context = {
        'registration_id': registration.pk,
        'assessment': assessment_object
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@ login_required
def prolonged_generalized_convulsive_seizures(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('prolonged_generalized_convulsive_seizures') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'prolonged_generalized_convulsive_seizures': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'prolonged_generalized_convulsive_seizures': False,
            'registration': registration
        })

    if created:
        assessment_object = created
    else:
        assessment_object = assessment

    context = {
        'registration_id': registration.pk,
        'assessment': assessment_object
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@ login_required
def experienced_prolonged_focal_seizures(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('experienced_prolonged_focal_seizures') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'experienced_prolonged_focal_seizures': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'experienced_prolonged_focal_seizures': False,
            'registration': registration
        })

    if created:
        assessment_object = created
    else:
        assessment_object = assessment

    context = {
        'registration_id': registration.pk,
        'assessment': assessment_object
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@ login_required
def assessment(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()
    sites = Site.objects.filter(registration=registration).all()

    active_surgical_site = None
    active_neurology_site = None
    active_general_paediatric_site = None

    historical_neurology_sites = Site.objects.filter(
        registration=registration, site_is_paediatric_neurology_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()
    historical_surgical_sites = Site.objects.filter(
        registration=registration, site_is_childrens_epilepsy_surgery_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()
    historical_general_paediatric_sites = Site.objects.filter(
        registration=registration, site_is_general_paediatric_centre=True, site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site

    # Site.objects.filter(registration=registration).delete()

    context = {
        "case_id": case_id,
        "registration": registration,
        "historical_neurology_sites": historical_neurology_sites,
        "historical_surgical_sites": historical_surgical_sites,
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_surgical_site": active_surgical_site,
        "active_neurology_site": active_neurology_site,
        "active_general_paediatric_site": active_general_paediatric_site,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "assessment",
        "all_my_sites": sites
    }
    return render(request=request, template_name='epilepsy12/assessment.html', context=context)
