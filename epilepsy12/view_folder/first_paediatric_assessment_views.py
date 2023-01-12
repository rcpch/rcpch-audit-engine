from django.contrib.auth.decorators import login_required, permission_required
from epilepsy12.constants import *
from ..common_view_functions import validate_and_update_model, recalculate_form_generate_response
from ..models import Registration, FirstPaediatricAssessment
from ..decorator import user_can_access_this_hospital_trust


@login_required
@user_can_access_this_hospital_trust()
def first_paediatric_assessment(request, case_id):
    registration = Registration.objects.get(case=case_id)

    if FirstPaediatricAssessment.objects.filter(registration=registration).exists():
        first_paediatric_assessment = FirstPaediatricAssessment.objects.filter(
            registration=registration).get()
    else:
        FirstPaediatricAssessment.objects.create(
            registration=registration
            # will autoupdate date and user on creation
        )
        first_paediatric_assessment = FirstPaediatricAssessment.objects.filter(
            registration=registration).get()

    context = {
        "case_id": case_id,
        "registration": registration,
        "first_paediatric_assessment": first_paediatric_assessment,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "audit_progress": registration.audit_progress,
        "active_template": "first_paediatric_assessment"
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template='epilepsy12/first_paediatric_assessment.html',
        context=context
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def first_paediatric_assessment_in_acute_or_nonacute_setting(request, first_paediatric_assessment_id):
    """
    HTMX callback from first_paediatric_assessment_in_acute_or_nonacute_setting partial, itself
    parent to single_choice_multiple_choice_toggle partial, whose button name stores the selected value
    On selection first_paediatric_assessment_in_acute_or_nonacute_setting partial is returned.
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='first_paediatric_assessment_in_acute_or_nonacute_setting',
            page_element='multiple_choice_multiple_toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "chronicity_selection": CHRONICITY,
        "first_paediatric_assessment": first_paediatric_assessment
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/first_paediatric_assessment_in_acute_or_nonacute_setting.html",
        context=context,
        error_message=error_message
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def has_number_of_episodes_since_the_first_been_documented(request, first_paediatric_assessment_id):
    """
    POST request from toggle in has_number_of_episodes_since_the_first_been_documented partial
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='has_number_of_episodes_since_the_first_been_documented',
            page_element='toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "first_paediatric_assessment": first_paediatric_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/when_the_first_epileptic_episode_occurred.html",
        context=context,
        error_message=error_message
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def general_examination_performed(request, first_paediatric_assessment_id):
    """
    POST request from toggle in has_general_examination_performed partial
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='general_examination_performed',
            page_element='toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "first_paediatric_assessment": first_paediatric_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/when_the_first_epileptic_episode_occurred.html",
        context=context,
        error_message=error_message
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def neurological_examination_performed(request, first_paediatric_assessment_id):
    """
    POST request from toggle in neurological_examination_performed partial
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='neurological_examination_performed',
            page_element='toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "first_paediatric_assessment": first_paediatric_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/when_the_first_epileptic_episode_occurred.html",
        context=context,
        error_message=error_message
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def developmental_learning_or_schooling_problems(request, first_paediatric_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='developmental_learning_or_schooling_problems',
            page_element='toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "first_paediatric_assessment": first_paediatric_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/when_the_first_epileptic_episode_occurred.html",
        context=context,
        error_message=error_message
    )

    return response


@login_required
@user_can_access_this_hospital_trust()
@permission_required('epilepsy12.change_first_paediatric_assessment', raise_exception=True)
def behavioural_or_emotional_problems(request, first_paediatric_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """
    try:
        error_message = None
        validate_and_update_model(
            request,
            first_paediatric_assessment_id,
            FirstPaediatricAssessment,
            field_name='behavioural_or_emotional_problems',
            page_element='toggle_button',
        )

    except ValueError as error:
        error_message = error

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        pk=first_paediatric_assessment_id)

    context = {
        "first_paediatric_assessment": first_paediatric_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = recalculate_form_generate_response(
        model_instance=first_paediatric_assessment,
        request=request,
        template="epilepsy12/partials/first_paediatric_assessment/when_the_first_epileptic_episode_occurred.html",
        context=context,
        error_message=error_message
    )

    return response
