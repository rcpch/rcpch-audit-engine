from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required

from epilepsy12.constants.user_types import CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE, CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE
from ..models import Registration, Assessment, Case, HospitalTrust, Site
from ..common_view_functions import validate_and_update_model, recalculate_form_generate_response


@login_required
@permission_required(CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE[0], raise_exception=True)
def consultant_paediatrician_referral_made(request, assessment_id):
    """
    POST request callback from toggle_button in consultant_paediatrician partial
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='consultant_paediatrician_referral_made',
            page_element='toggle_button',
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # tidy up
    if assessment.consultant_paediatrician_referral_made == False:
        Assessment.objects.filter(pk=assessment_id).update(
            consultant_paediatrician_referral_date=None,
            consultant_paediatrician_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

        # refresh all objects and return
        assessment = Assessment.objects.get(pk=assessment_id)

        # if any allocated sites make them historical
        if Site.objects.filter(
            case=assessment.registration.case,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_general_paediatric_centre=True
        ).exists():
            Site.objects.filter(case=assessment.registration.case,
                                site_is_actively_involved_in_epilepsy_care=True,
                                site_is_general_paediatric_centre=True).update(site_is_actively_involved_in_epilepsy_care=False)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        'assessment': assessment,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def consultant_paediatrician_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='consultant_paediatrician_referral_date',
            page_element='date_field',
            comparison_date_field_name='consultant_paediatrician_input_date',
            is_earliest_date=True
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": False,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def consultant_paediatrician_input_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician input date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='consultant_paediatrician_input_date',
            page_element='date_field',
            comparison_date_field_name='consultant_paediatrician_referral_date',
            is_earliest_date=False
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response

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

    # if this registration already has a record in sites
    #  associated with this hospital,
    # update it include general paediatrics, else create a new record
    if Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=general_paediatric_centre).exists():
        Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=general_paediatric_centre).update(
                site_is_general_paediatric_centre=True,
                site_is_actively_involved_in_epilepsy_care=True,
                updated_at=timezone.now(),
                updated_by=request.user
        )
    else:
        site = Site.objects.create(
            case=assessment.registration.case,
            hospital_trust=general_paediatric_centre,
            site_is_primary_centre_of_epilepsy_care=False,
            site_is_childrens_epilepsy_surgery_centre=False,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_paediatric_neurology_centre=False,
            site_is_general_paediatric_centre=True,
        )
        site.save()

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def edit_general_paediatric_centre(request, assessment_id, site_id):
    """
    HTMX call back from consultant_paediatrician partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """

    selected_general_paediatric_centre_id = request.POST.get(
        'edit_general_paediatric_centre')

    new_hospital_trust = HospitalTrust.objects.get(
        pk=selected_general_paediatric_centre_id)

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        case=assessment.registration.case,
        hospital_trust=new_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=new_hospital_trust,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        site.site_is_general_paediatric_centre = True
        site.updated_at = timezone.now(),
        site.updated_by = request.user
        site.save()
        Site.objects.get(pk=site_id).delete()

    else:
        # this change is a new hospital
        Site.objects.filter(pk=site_id).update(
            hospital_trust=new_hospital_trust,
            site_is_general_paediatric_centre=True,
            site_is_actively_involved_in_epilepsy_care=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def update_general_paediatric_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from consultant_paediatrician partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the general_paediatric_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the hospital_list dropdown partial
    """

    assessment = Assessment.objects.get(pk=assessment_id)

    general_paediatric_edit_active = True
    if action == 'cancel':
        general_paediatric_edit_active = False

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": general_paediatric_edit_active,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
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

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": False,
        "error": error_message,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


"""
*** Paediatric neurology ***
"""


@login_required
@permission_required(CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE[0], raise_exception=True)
def paediatric_neurologist_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model_id=assessment_id,
            model=Assessment,
            field_name='paediatric_neurologist_referral_made',
            page_element='toggle_button'
        )
    except ValueError as error:
        error_message = error

    # get new instance of Assessment
    assessment = Assessment.objects.get(pk=assessment_id)

    # if there is no Paediatric neurologist - set all associated fields to None
    if assessment.paediatric_neurologist_referral_made == False:

        Assessment.objects.filter(pk=assessment_id).update(
            paediatric_neurologist_referral_date=None,
            paediatric_neurologist_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

        # get new instance of Assessment
        assessment = Assessment.objects.get(pk=assessment_id)

        # if any allocated sites make them historical
        if Site.objects.filter(
            case=assessment.registration.case,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_paediatric_neurology_centre=True
        ).exists():
            Site.objects.filter(case=assessment.registration.case,
                                site_is_actively_involved_in_epilepsy_care=True,
                                site_is_paediatric_neurology_centre=True).update(site_is_actively_involved_in_epilepsy_care=False)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def paediatric_neurologist_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='paediatric_neurologist_referral_date',
            page_element='date_field',
            comparison_date_field_name='paediatric_neurologist_input_date',
            is_earliest_date=True
        )
    except ValueError as error:
        error_message = error

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def paediatric_neurologist_input_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='paediatric_neurologist_input_date',
            page_element='date_field',
            comparison_date_field_name='paediatric_neurologist_referral_date',
            is_earliest_date=False
        )
    except ValueError as error:
        error_message = error

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response

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

    # if this registration already has a record in sites
    #  associated with this hospital,
    # update it include paediatric neurology, else create a new record
    if Site.objects.filter(case=assessment.registration.case, hospital_trust=paediatric_neurology_centre).exists():
        Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=paediatric_neurology_centre).update(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_paediatric_neurology_centre=True,
                updated_at=timezone.now(),
                updated_by=request.user
        )
    else:
        site = Site.objects.create(
            case=assessment.registration.case,
            hospital_trust=paediatric_neurology_centre,
            site_is_primary_centre_of_epilepsy_care=False,
            site_is_childrens_epilepsy_surgery_centre=False,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_paediatric_neurology_centre=True,
            site_is_general_paediatric_centre=False,
        )
        site.save()

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def edit_paediatric_neurology_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """
    paediatric_neurology_centre = HospitalTrust.objects.get(
        pk=request.POST.get('edit_paediatric_neurology_centre'))

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        case=assessment.registration.case,
        hospital_trust=paediatric_neurology_centre,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=paediatric_neurology_centre,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        site.site_is_paediatric_neurology_centre = True
        site.save()
        Site.objects.get(pk=site_id).delete()

    else:
        # this change is a new hospital
        Site.objects.filter(pk=site_id).update(
            hospital_trust=paediatric_neurology_centre,
            site_is_paediatric_neurology_centre=True,
            site_is_actively_involved_in_epilepsy_care=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def update_paediatric_neurology_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from paediatric_neurology partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the neurology_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the hospital_list dropdown partial
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    neurology_edit_active = True
    if action == 'cancel':
        neurology_edit_active = False

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "neurology_edit_active": neurology_edit_active,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
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

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": error_message,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


"""
** Children's epilepsy surgery service **
"""


@login_required
def childrens_epilepsy_surgical_service_referral_criteria_met(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='childrens_epilepsy_surgical_service_referral_criteria_met',
            page_element='toggle_button',
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)
    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "hospital_list": hospital_list
    }

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def childrens_epilepsy_surgical_service_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model_id=assessment_id,
            model=Assessment,
            field_name='childrens_epilepsy_surgical_service_referral_made',
            page_element='toggle_button'
        )
    except ValueError as error:
        error_message = error

    # get new instance of Assessment
    assessment = Assessment.objects.get(pk=assessment_id)

    # A surgical referral has not been made - set all fields related fields to None
    if assessment.childrens_epilepsy_surgical_service_referral_made == False:
        Assessment.objects.filter(pk=assessment_id).update(
            childrens_epilepsy_surgical_service_referral_date=None,
            childrens_epilepsy_surgical_service_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

        # get new instance of Assessment
        assessment = Assessment.objects.get(pk=assessment_id)

        # if any allocated sites make them historical
        if Site.objects.filter(
            case=assessment.registration.case,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_childrens_epilepsy_surgery_centre=True
        ).exists():
            Site.objects.filter(case=assessment.registration.case,
                                site_is_actively_involved_in_epilepsy_care=True,
                                site_is_childrens_epilepsy_surgery_centre=True).update(site_is_actively_involved_in_epilepsy_care=False)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='childrens_epilepsy_surgical_service_referral_date',
            page_element='date_field',
            comparison_date_field_name='childrens_epilepsy_surgical_service_input_date',
            is_earliest_date=True
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        'assessment': assessment,
        "surgery_edit_active": False,
        "error": None,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='childrens_epilepsy_surgical_service_input_date',
            page_element='date_field',
            comparison_date_field_name='childrens_epilepsy_surgical_service_referral_date',
            is_earliest_date=False
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        'assessment': assessment,
        "surgery_edit_active": False,
        "error": None,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
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

    # if this registration already has a record in sites
    #  associated with this hospital,
    # update it to include epilepsy surgery, else create a new record
    if Site.objects.filter(case=assessment.registration.case, hospital_trust=epilepsy_surgery_centre).exists():
        Site.objects.filter(
            case=assessment.registration.case,
            hospital_trust=epilepsy_surgery_centre).update(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_childrens_epilepsy_surgery_centre=True,
                updated_at=timezone.now(),
                updated_by=request.user
        )
    else:
        site = Site.objects.create(
            case=assessment.registration.case,
            hospital_trust=epilepsy_surgery_centre,
            site_is_primary_centre_of_epilepsy_care=False,
            site_is_childrens_epilepsy_surgery_centre=True,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_paediatric_neurology_centre=False,
            site_is_general_paediatric_centre=False,
        )
        site.save()

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def edit_epilepsy_surgery_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template.
    This is a POST request on button click.
    It updates the Site object with the new centre and returns
    the same partial template.
    """
    new_hospital_trust = HospitalTrust.objects.get(
        pk=request.POST.get('edit_epilepsy_surgery_centre'))

    assessment = Assessment.objects.get(pk=assessment_id)

    if Site.objects.filter(
        case=assessment.registration.case,
        hospital_trust=new_hospital_trust,
        site_is_actively_involved_in_epilepsy_care=True
    ).exists():
        # this hospital trust already exists for this registration
        # update that record, delete this

        site = Site.objects.filter(
            case=assessment.registration.case,
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
            site_is_actively_involved_in_epilepsy_care=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
def update_epilepsy_surgery_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from epilepsy_surgery partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the surgery_edit_active flag
    It returns the partial template with the updated flag.
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    surgery_edit_active = True
    if action == 'cancel':
        surgery_edit_active = False

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "surgery_edit_active": surgery_edit_active,
        "error": None,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


@login_required
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

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "surgery_edit_active": False,
        "error": error_message,
        'hospital_list': hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


"""
*** Epilepsy Nurse Specialist ***
"""


@login_required
def epilepsy_specialist_nurse_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='epilepsy_specialist_nurse_referral_made',
            page_element='toggle_button',
        )
    except ValueError as error:
        error_message = error

    # There is no(longer) epilepsy nurse referral in place - set all epilepsy nurse related fields to None
    if Assessment.objects.filter(pk=assessment_id, epilepsy_specialist_nurse_referral_made=False).exists():
        Assessment.objects.filter(pk=assessment_id, epilepsy_specialist_nurse_referral_made=False).update(
            epilepsy_specialist_nurse_referral_date=None,
            epilepsy_specialist_nurse_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def epilepsy_specialist_nurse_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='epilepsy_specialist_nurse_referral_date',
            page_element='date_field',
            comparison_date_field_name='epilepsy_specialist_nurse_input_date',
            is_earliest_date=True
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def epilepsy_specialist_nurse_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name='epilepsy_specialist_nurse_input_date',
            page_element='date_field',
            comparison_date_field_name='epilepsy_specialist_nurse_referral_date',
            is_earliest_date=False
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


@login_required
def assessment(request, case_id):

    case = Case.objects.get(pk=case_id)
    registration = Registration.objects.filter(case=case).get()

    # create an assessment object if one does not exist
    if not Assessment.objects.filter(registration=registration).exists():

        # create an assessment object
        Assessment.objects.create(
            registration=registration
        )

    assessment = Assessment.objects.filter(registration=registration).get()

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')

    context = {
        "case_id": case_id,
        "assessment": assessment,
        "registration": assessment.registration,
        "audit_progress": registration.audit_progress,
        "active_template": "assessment",
        "hospital_list": hospital_list
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(
        assessment.registration.case)

    context.update(sites_context)

    template_name = 'epilepsy12/assessment.html'

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context
    )

    return response


def add_sites_and_site_history_to_context(case):
    sites = Site.objects.filter(case=case).all()

    active_surgical_site = None
    active_neurology_site = None
    active_general_paediatric_site = None

    historical_neurology_sites = Site.objects.filter(
        case=case,
        site_is_paediatric_neurology_centre=True,
        site_is_actively_involved_in_epilepsy_care=False).all()
    historical_surgical_sites = Site.objects.filter(
        case=case,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_actively_involved_in_epilepsy_care=False).all()
    historical_general_paediatric_sites = Site.objects.filter(
        case=case,
        site_is_general_paediatric_centre=True,
        site_is_actively_involved_in_epilepsy_care=False).all()

    for site in sites:
        if site.site_is_actively_involved_in_epilepsy_care:
            if site.site_is_childrens_epilepsy_surgery_centre:
                active_surgical_site = site
            if site.site_is_paediatric_neurology_centre:
                active_neurology_site = site
            if site.site_is_general_paediatric_centre:
                active_general_paediatric_site = site
    context = {
        "historical_neurology_sites": historical_neurology_sites,
        "historical_surgical_sites": historical_surgical_sites,
        "historical_general_paediatric_sites": historical_general_paediatric_sites,
        "active_surgical_site": active_surgical_site,
        "active_neurology_site": active_neurology_site,
        "active_general_paediatric_site": active_general_paediatric_site,
        "all_my_sites": sites,
    }

    return context
