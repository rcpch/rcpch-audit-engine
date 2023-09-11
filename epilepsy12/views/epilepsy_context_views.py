from django.contrib.auth.decorators import permission_required
from ..decorator import user_may_view_this_child, login_and_otp_required
from epilepsy12.constants.common import OPT_OUT_UNCERTAIN
from ..models import EpilepsyContext, Registration, Site
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.view_epilepsycontext", raise_exception=True)
def epilepsy_context(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    epilepsy_context, created = EpilepsyContext.objects.get_or_create(
        registration=registration
    )

    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    context = {
        "case_id": case_id,
        "registration": registration,
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
        "audit_progress": epilepsy_context.registration.audit_progress,
        "active_template": "epilepsy_context",
        "organisation_id": organisation_id,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/epilepsy_context.html",
        context=context,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def previous_febrile_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="previous_febrile_seizure",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_febrile_seizure.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def previous_acute_symptomatic_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="previous_acute_symptomatic_seizure",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_acute_symptomatic_seizure.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def is_there_a_family_history_of_epilepsy(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="is_there_a_family_history_of_epilepsy",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/is_there_a_family_history_of_epilepsy.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def previous_neonatal_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="previous_neonatal_seizures",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_neonatal_seizures.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def were_any_of_the_epileptic_seizures_convulsive(request, epilepsy_context_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="were_any_of_the_epileptic_seizures_convulsive",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/were_any_of_the_epileptic_seizures_convulsive.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def experienced_prolonged_generalized_convulsive_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the experienced_prolonged_generalized_convulsive_seizures partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="experienced_prolonged_generalized_convulsive_seizures",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/experienced_prolonged_generalized_convulsive_seizures.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def experienced_prolonged_focal_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the experienced_prolonged_focal_seizures partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="experienced_prolonged_focal_seizures",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/experienced_prolonged_focal_seizures.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_epilepsycontext", raise_exception=True)
def diagnosis_of_epilepsy_withdrawn(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial,
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            epilepsy_context_id,
            EpilepsyContext,
            field_name="diagnosis_of_epilepsy_withdrawn",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {"epilepsy_context": epilepsy_context}

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/epilepsy_diagnosis_withdrawn.html",
        context=context,
        error_message=error_message,
    )

    return response
