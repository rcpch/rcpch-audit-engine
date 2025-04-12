from django.utils import timezone
from django.contrib.auth.decorators import permission_required

from ..models import Registration, Assessment, Case, Organisation, Site
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child, login_and_otp_required


def update_site_model(
    centre_role: str, selected_organisation, case, user, site_id=None
):
    """
    Helper function to update sites model with attributes describing role of site
    (general paediatric, neurology, surgical centre)
    This is complicated because historical records of lead centre status are persisted
    whereas historical records of other roles are not.

    If the organisation is the lead site for this child, and also the neurology/surgery
    or general paediatric centre, all this information can be stored in one record.

    If the organisation used to be the lead site for this child, and now is actively
    the neurology/surgery or general paediatric centre, two records are stored: one where
    site_is_actively_involved_in_epilepsy_care is False and site_is_primary_centre_of_epilepsy_care is True,
    the other where site_is_actively_involved_in_epilepsy_care is True and one/some of the other attributes
    is True. site_is_primary_centre_of_epilepsy_care here is False.
    """

    if centre_role == "general_paediatric_centre":
        update_fields = {
            "site_is_general_paediatric_centre": True,
        }
        reverse_update_fields = {
            "site_is_general_paediatric_centre": False,
        }
    elif centre_role == "paediatric_neurology_centre":
        update_fields = {
            "site_is_paediatric_neurology_centre": True,
        }
        reverse_update_fields = {
            "site_is_paediatric_neurology_centre": False,
        }
    elif centre_role == "epilepsy_surgery_centre":
        update_fields = {
            "site_is_childrens_epilepsy_surgery_centre": True,
        }
        reverse_update_fields = {
            "site_is_childrens_epilepsy_surgery_centre": False,
        }

    # selected_organisation has never been involved in child's care
    if not Site.objects.filter(
        case=case,
        organisation=selected_organisation,
    ).exists():
        # ensure that no other existing organisation is still providing this care
        Site.objects.filter(
            case=case, site_is_actively_involved_in_epilepsy_care=True
        ).update(**reverse_update_fields)

        # create new site
        Site.objects.create(
            case=case,
            organisation=selected_organisation,
            site_is_primary_centre_of_epilepsy_care=False,
            updated_at=timezone.now(),
            updated_by=user,
            site_is_actively_involved_in_epilepsy_care=True,
            active_transfer=False,
            transfer_origin_organisation=None,
            transfer_request_date=None,
            **update_fields
        )
    else:
        # selected organisation is or has has been already involved in this child's care

        # selected_organisation is active lead centre
        if Site.objects.filter(
            case=case,
            organisation=selected_organisation,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
        ).exists():
            # there can be only one of these

            Site.objects.filter(
                case=case,
                organisation=selected_organisation,
                site_is_primary_centre_of_epilepsy_care=True,
                site_is_actively_involved_in_epilepsy_care=True,
            ).update(
                **update_fields
            )  # update only the status requested

        # selected_organisation was previously lead centre
        elif Site.objects.filter(
            case=case,
            organisation=selected_organisation,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=False,
        ).exists():
            # create a new centre to be actively involved in care but
            # not be primary centre. This allows historical lead centres to be recorded

            Site.objects.create(
                case=case,
                organisation=selected_organisation,
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_primary_centre_of_epilepsy_care=False,
                **update_fields
            )

        # selected_organisation was previously actively involved in care but not as primary centre
        elif Site.objects.filter(
            case=case,
            organisation=selected_organisation,
            site_is_primary_centre_of_epilepsy_care=False,
            site_is_actively_involved_in_epilepsy_care=False,
        ).exists():
            # reactivate record and update for new role

            Site.objects.filter(
                case=case,
                organisation=selected_organisation,
                site_is_primary_centre_of_epilepsy_care=False,
                site_is_actively_involved_in_epilepsy_care=False,
            ).update(site_is_actively_involved_in_epilepsy_care=True, **update_fields)

        # selected_organisation is actively involved in care but not as primary centre
        elif Site.objects.filter(
            case=case,
            organisation=selected_organisation,
            site_is_primary_centre_of_epilepsy_care=False,
            site_is_actively_involved_in_epilepsy_care=True,
        ).exists():
            # update role

            Site.objects.filter(
                case=case,
                organisation=selected_organisation,
                site_is_primary_centre_of_epilepsy_care=False,
                site_is_actively_involved_in_epilepsy_care=True,
            ).update(**update_fields)

    if site_id is not None:
        # must delete the old record if this is an edit
        old_site = Site.objects.get(pk=site_id)
        if old_site.site_is_primary_centre_of_epilepsy_care == False:
            old_site.delete()


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
            field_name="consultant_paediatrician_referral_made",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # tidy up
    if assessment.consultant_paediatrician_referral_made == False:
        Assessment.objects.filter(pk=assessment_id).update(
            consultant_paediatrician_referral_date=None,
            consultant_paediatrician_input_achieved=None,
            consultant_paediatrician_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # if any allocated sites remove them
    if Site.objects.filter(
        case=assessment.registration.case,
        site_is_general_paediatric_centre=True,
    ).exists():
        # loop through these and delete any site where the organisation
        # is not used elsewhere for this child actively for any other attribute (surgery or neurology)
        # or is not a historical or active lead site. If it is, set site_is_general_paediatric_centre to False
        updated_general_paediatric_status_sites = Site.objects.filter(
            case=assessment.registration.case,
            site_is_general_paediatric_centre=True,
        )
        for site in updated_general_paediatric_status_sites:
            if (
                site.site_is_primary_centre_of_epilepsy_care == True
                or (
                    site.site_is_paediatric_neurology_centre
                    or site.site_is_childrens_epilepsy_surgery_centre
                )
                and site.site_is_general_paediatric_centre
            ):
                site.site_is_general_paediatric_centre = False
                site.save(update_fields=["site_is_general_paediatric_centre"])
            else:
                site.delete()

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {"assessment": assessment, "organisation_list": organisation_list}

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def consultant_paediatrician_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="consultant_paediatrician_referral_date",
            page_element="date_field",
            comparison_date_field_name="consultant_paediatrician_input_date",
            is_earliest_date=True,
            earliest_allowable_date=assessment.registration.case.date_of_birth,
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def consultant_paediatrician_input_achieved(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in input achieved toggle in the partial, generating a post request.
    This shows or hides the consultant paediatrician input date value, and returns the same partial.
    It updates the model with the input achieved value
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            assessment_id,
            Assessment,
            field_name="consultant_paediatrician_input_achieved",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    assessment = Assessment.objects.get(pk=assessment_id)

    # if the input is not achieved, set the input date to None
    if assessment.consultant_paediatrician_input_achieved == False:
        Assessment.objects.filter(pk=assessment_id).update(
            consultant_paediatrician_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def consultant_paediatrician_input_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician input date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="consultant_paediatrician_input_date",
            page_element="date_field",
            comparison_date_field_name="consultant_paediatrician_referral_date",
            is_earliest_date=False,
            earliest_allowable_date=assessment.registration.assessment.consultant_paediatrician_referral_date,
        )
    except ValueError as error:
        error_message = error

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


# centre CRUD


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def general_paediatric_centre(request, assessment_id):
    """
    HTMX call back from organisation_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to organisation_list partial from
    consultant_paediatrician partial which is its parent
    """

    general_paediatric_centre = Organisation.objects.get(
        pk=request.POST.get("general_paediatric_centre")
    )
    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="general_paediatric_centre",
        selected_organisation=general_paediatric_centre,
        case=assessment.registration.case,
        user=request.user,
    )

    # filter list to include only NHS organisations
    organisation_list = (
        Organisation.objects.filter(active=True)
        .order_by("name")
        .exclude(pk=general_paediatric_centre.pk)
    )

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def edit_general_paediatric_centre(request, assessment_id, site_id):
    """
    HTMX call back from consultant_paediatrician partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """

    general_paediatric_centre = Organisation.objects.get(
        pk=request.POST.get("edit_general_paediatric_centre")
    )

    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="general_paediatric_centre",
        selected_organisation=general_paediatric_centre,
        case=assessment.registration.case,
        user=request.user,
        site_id=site_id,
    )

    # filter list to include only NHS organisations
    organisation_list = (
        Organisation.objects.filter(active=True)
        .order_by("name")
        .exclude(pk=general_paediatric_centre.pk)
    )

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "general_paediatric_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def update_general_paediatric_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from consultant_paediatrician partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the general_paediatric_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the organisation_list dropdown partial
    """

    assessment = Assessment.objects.get(pk=assessment_id)

    general_paediatric_edit_active = True
    if action == "cancel":
        general_paediatric_edit_active = False

    selected_site = Site.objects.get(pk=site_id)

    # filter list to include only NHS organisations
    organisation_list = (
        Organisation.objects.filter(active=True)
        .order_by("name")
        .exclude(pk=selected_site.organisation.pk)
    )

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": general_paediatric_edit_active,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def delete_general_paediatric_centre(request, assessment_id, site_id):
    """
    HTMX call back from organisations_select partial template.
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
        associated_site.site_is_primary_centre_of_epilepsy_care
        or associated_site.site_is_paediatric_neurology_centre
        or associated_site.site_is_childrens_epilepsy_surgery_centre
    ):
        # this site also delivers (or has delivered) surgical or general paediatric care
        # update to remove general paeds
        Site.objects.filter(pk=associated_site.pk).update(
            site_is_general_paediatric_centre=False
        )

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "general_paediatric_edit_active": False,
        "error": error_message,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/consultant_paediatrician.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


"""
*** Paediatric neurology ***
"""


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
            field_name="paediatric_neurologist_referral_made",
            page_element="toggle_button",
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
            paediatric_neurologist_input_achieved=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

        # get new instance of Assessment
        assessment = Assessment.objects.get(pk=assessment_id)

        if Site.objects.filter(
            case=assessment.registration.case, site_is_paediatric_neurology_centre=True
        ).exists():
            updated_neurology_status_sites = Site.objects.filter(
                case=assessment.registration.case,
                site_is_paediatric_neurology_centre=True,
            )
            for site in updated_neurology_status_sites:
                if (
                    site.site_is_primary_centre_of_epilepsy_care == True
                    or (
                        site.site_is_general_paediatric_centre
                        or site.site_is_childrens_epilepsy_surgery_centre
                    )
                    and site.site_is_general_paediatric_centre
                ):
                    site.site_is_paediatric_neurology_centre = False
                    site.save(update_fields=["site_is_paediatric_neurology_centre"])
                else:
                    site.delete()

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {"assessment": assessment, "organisation_list": organisation_list}

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def paediatric_neurologist_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="paediatric_neurologist_referral_date",
            page_element="date_field",
            comparison_date_field_name="paediatric_neurologist_input_date",
            is_earliest_date=True,
            earliest_allowable_date=assessment.registration.first_paediatric_assessment_date,
        )
    except ValueError as error:
        error_message = error

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def paediatric_neurologist_input_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="paediatric_neurologist_input_date",
            page_element="date_field",
            comparison_date_field_name="paediatric_neurologist_referral_date",
            is_earliest_date=False,
            earliest_allowable_date=assessment.paediatric_neurologist_referral_date,
        )
    except ValueError as error:
        error_message = error

    # get fresh list of all sites associated with registration
    # which are organised for the template to filtered to share all active
    # and inactive neurology centres

    assessment = Assessment.objects.get(pk=assessment_id)

    # an input date has been made so set the not achieved flag to False
    assessment.paediatric_neurologist_input_not_achieved = False
    assessment.save(update_fields=["paediatric_neurologist_input_achieved"])

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def paediatric_neurologist_input_achieved(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in input achieved toggle in the partial, generating a post request.
    This shows or hides the paediatric neurologist input date value, and returns the same partial.
    It updates the model with the input achieved value
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            assessment_id,
            Assessment,
            field_name="paediatric_neurologist_input_achieved",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    assessment = Assessment.objects.get(pk=assessment_id)

    # if the input is not achieved, set the input date to None
    if assessment.paediatric_neurologist_input_achieved == False:
        Assessment.objects.filter(pk=assessment_id).update(
            paediatric_neurologist_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


# paediatric neurology centre selection


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def paediatric_neurology_centre(request, assessment_id):
    """
    HTMX call back from organisation_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to organisation_list partial from
    epilepsy_surgery partial which is its parent
    """
    paediatric_neurology_centre = Organisation.objects.get(
        pk=request.POST.get("paediatric_neurology_centre")
    )
    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="paediatric_neurology_centre",
        selected_organisation=paediatric_neurology_centre,
        case=assessment.registration.case,
        user=request.user,
    )

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def edit_paediatric_neurology_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template. This is a POST request on button click.
    It updates the Site object and returns the same partial template.
    """
    paediatric_neurology_centre = Organisation.objects.get(
        pk=request.POST.get("edit_paediatric_neurology_centre")
    )

    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="paediatric_neurology_centre",
        selected_organisation=paediatric_neurology_centre,
        case=assessment.registration.case,
        user=request.user,
        site_id=site_id,
    )

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "neurology_edit_active": False,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def update_paediatric_neurology_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from paediatric_neurology partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the neurology_edit_active flag
    It returns the partial template with the updated flag.
    Note it does not update the record - only toggles the cancel button and
    shows/hides the organisation_list dropdown partial
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    neurology_edit_active = True
    if action == "cancel":
        neurology_edit_active = False

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "neurology_edit_active": neurology_edit_active,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
        associated_site.site_is_primary_centre_of_epilepsy_care
        or associated_site.site_is_general_paediatric_centre
        or associated_site.site_is_childrens_epilepsy_surgery_centre
    ):
        # this site also delivers (or has delivered) surgical or general paediatric care
        # update to remove general paeds
        Site.objects.filter(pk=associated_site.pk).update(
            site_is_paediatric_neurology_centre=False
        )

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": error_message,
        "organisation_list": organisation_list,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/paediatric_neurology.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


"""
** Children's epilepsy surgery service **
"""


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
            field_name="childrens_epilepsy_surgical_service_referral_criteria_met",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)
    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
            field_name="childrens_epilepsy_surgical_service_referral_made",
            page_element="toggle_button",
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
            updated_by=request.user,
        )

        # get new instance of Assessment
        assessment = Assessment.objects.get(pk=assessment_id)

        if Site.objects.filter(
            case=assessment.registration.case,
            site_is_childrens_epilepsy_surgery_centre=True,
        ).exists():
            # loop through these and delete any site where the organisation
            # is not used elsewhere for this child actively for any other attribute (general paediatric or neurology)
            # or is not a historical or active lead site. If it is, set site_is_childrens_epilepsy_surgery_centre to False
            updated_surgery_status_sites = Site.objects.filter(
                case=assessment.registration.case,
                site_is_childrens_epilepsy_surgery_centre=True,
            )
            for site in updated_surgery_status_sites:
                if (
                    site.site_is_primary_centre_of_epilepsy_care == True
                    or (
                        site.site_is_general_paediatric_centre
                        or site.site_is_paediatric_neurology_centre
                    )
                    and site.site_is_general_paediatric_centre
                ):
                    site.site_is_childrens_epilepsy_surgery_centre = False
                    site.save(
                        update_fields=["site_is_childrens_epilepsy_surgery_centre"]
                    )
                else:
                    site.delete()

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="childrens_epilepsy_surgical_service_referral_date",
            page_element="date_field",
            comparison_date_field_name="childrens_epilepsy_surgical_service_input_date",
            is_earliest_date=True,
            earliest_allowable_date=assessment.registration.first_paediatric_assessment_date,
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def childrens_epilepsy_surgical_service_review_date_status(
    request, assessment_id, status
):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    This toggles show/hide on the childrens_epilepsy_surgical_service_input_date field as
    this is not a mandatory field.
    Accepts status (string) values of 'known' and 'unknown'
    """
    error_message = None

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    except Exception as e:
        error_message = e

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    if status == "unknown":
        # remove any previously stored surgical review date
        assessment.childrens_epilepsy_surgical_service_input_date = None
        assessment.save()

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": status == "known",
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="childrens_epilepsy_surgical_service_input_date",
            page_element="date_field",
            comparison_date_field_name="childrens_epilepsy_surgical_service_referral_date",
            is_earliest_date=False,
            earliest_allowable_date=assessment.childrens_epilepsy_surgical_service_referral_date,
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def epilepsy_surgery_centre(request, assessment_id):
    """
    HTMX call back from organisation_list partial.
    POST request to update/save centre in Site model
    assessment_id passed to organisation_list partial from
    epilepsy_surgery partial which is its parent
    """
    epilepsy_surgery_centre = Organisation.objects.get(
        pk=request.POST.get("epilepsy_surgery_centre")
    )
    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="epilepsy_surgery_centre",
        selected_organisation=epilepsy_surgery_centre,
        case=assessment.registration.case,
        user=request.user,
    )

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def edit_epilepsy_surgery_centre(request, assessment_id, site_id):
    """
    HTMX call back from epilepsy_surgery partial template.
    This is a POST request on button click.
    It updates the Site object with the new centre and returns
    the same partial template.
    """
    epilepsy_surgery_centre = Organisation.objects.get(
        pk=request.POST.get("edit_epilepsy_surgery_centre")
    )

    assessment = Assessment.objects.get(pk=assessment_id)

    update_site_model(
        centre_role="epilepsy_surgery_centre",
        selected_organisation=epilepsy_surgery_centre,
        case=assessment.registration.case,
        user=request.user,
        site_id=site_id,
    )

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": assessment,
        "surgery_edit_active": False,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def update_epilepsy_surgery_centre_pressed(request, assessment_id, site_id, action):
    """
    HTMX callback from epilepsy_surgery partial on click of Update or Cancel
    (action is 'edit' or 'cancel') to change the surgery_edit_active flag
    It returns the partial template with the updated flag.
    """
    assessment = Assessment.objects.get(pk=assessment_id)

    surgery_edit_active = True
    if action == "cancel":
        surgery_edit_active = False

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "surgery_edit_active": surgery_edit_active,
        "error": None,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
        associated_site.site_is_primary_centre_of_epilepsy_care
        or associated_site.site_is_general_paediatric_centre
        or associated_site.site_is_paediatric_neurology_centre
    ):
        # this site also delivers (or has delivered) neurology or general paediatric care
        # update to remove surgery
        Site.objects.filter(pk=associated_site.pk).update(
            site_is_childrens_epilepsy_surgery_centre=False
        )

    else:
        # there are no other associated centres with this record: can delete
        Site.objects.filter(pk=associated_site.pk).delete()

    # refresh all objects and return
    assessment = Assessment.objects.get(pk=assessment_id)

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "assessment": Assessment.objects.get(pk=assessment_id),
        "surgery_edit_active": False,
        "error": error_message,
        "organisation_list": organisation_list,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/partials/assessment/epilepsy_surgery.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
    )

    return response


"""
*** Epilepsy Nurse Specialist ***
"""


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
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
            field_name="epilepsy_specialist_nurse_referral_made",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    # There is no(longer) epilepsy nurse referral in place - set all epilepsy nurse related fields to None
    if Assessment.objects.filter(
        pk=assessment_id, epilepsy_specialist_nurse_referral_made=False
    ).exists():
        Assessment.objects.filter(
            pk=assessment_id, epilepsy_specialist_nurse_referral_made=False
        ).update(
            epilepsy_specialist_nurse_referral_date=None,
            epilepsy_specialist_nurse_input_date=None,
            epilepsy_specialist_nurse_input_achieved=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {"assessment": assessment}

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def epilepsy_specialist_nurse_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="epilepsy_specialist_nurse_referral_date",
            page_element="date_field",
            comparison_date_field_name="epilepsy_specialist_nurse_input_date",
            is_earliest_date=True,
            earliest_allowable_date=assessment.registration.case.date_of_birth,
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {"assessment": assessment}

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def epilepsy_specialist_nurse_input_achieved(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in the input achieved toggle in the partial, generating a post request.
    This persists the epilepsy nurse specialist input achieved value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            assessment_id,
            Assessment,
            field_name="epilepsy_specialist_nurse_input_achieved",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    # if the input is not achieved, set the input date to None
    if assessment.epilepsy_specialist_nurse_input_achieved == False:
        Assessment.objects.filter(pk=assessment_id).update(
            epilepsy_specialist_nurse_input_date=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    context = {
        "assessment": assessment,
    }

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.change_assessment", raise_exception=True)
@user_may_view_this_child()
def epilepsy_specialist_nurse_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Assessment,
            model_id=assessment_id,
            field_name="epilepsy_specialist_nurse_input_date",
            page_element="date_field",
            comparison_date_field_name="epilepsy_specialist_nurse_referral_date",
            is_earliest_date=False,
            earliest_allowable_date=assessment.epilepsy_specialist_nurse_referral_date,
        )
    except ValueError as error:
        error_message = error

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {"assessment": assessment}

    template_name = "epilepsy12/partials/assessment/epilepsy_nurse.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@permission_required("epilepsy12.view_assessment", raise_exception=True)
@user_may_view_this_child()
def assessment(request, case_id):
    case = Case.objects.get(pk=case_id)
    registration = Registration.objects.filter(case=case).get()

    # create an assessment object if one does not exist
    if not Assessment.objects.filter(registration=registration).exists():
        # create an assessment object
        Assessment.objects.create(registration=registration)

    assessment = Assessment.objects.filter(registration=registration).get()

    # filter list to include only NHS organisations
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    context = {
        "case_id": case_id,
        "assessment": assessment,
        "registration": assessment.registration,
        "audit_progress": registration.audit_progress,
        "active_template": "assessment",
        "organisation_list": organisation_list,
        "organisation_id": organisation_id,
        "show_input_date": assessment.childrens_epilepsy_surgical_service_input_date
        is not None,
    }

    # add previous and current sites to context
    sites_context = add_sites_and_site_history_to_context(assessment.registration.case)

    context.update(sites_context)

    template_name = "epilepsy12/assessment.html"

    response = recalculate_form_generate_response(
        model_instance=assessment,
        request=request,
        template=template_name,
        context=context,
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
        site_is_actively_involved_in_epilepsy_care=False,
    ).all()
    historical_surgical_sites = Site.objects.filter(
        case=case,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_actively_involved_in_epilepsy_care=False,
    ).all()
    historical_general_paediatric_sites = Site.objects.filter(
        case=case,
        site_is_general_paediatric_centre=True,
        site_is_actively_involved_in_epilepsy_care=False,
    ).all()

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
