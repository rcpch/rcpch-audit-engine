from django.contrib.auth.decorators import login_required
from ..decorator import group_required, update_model
from epilepsy12.constants import *
from .common_view_functions import recalculate_form_generate_response

from ..models import Registration
from ..models import FirstPaediatricAssessment


@login_required
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
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'first_paediatric_assessment_in_acute_or_nonacute_setting', 'multiple_choice_multiple_toggle_button')
def first_paediatric_assessment_in_acute_or_nonacute_setting(request, first_paediatric_assessment_id):
    """
    HTMX callback from first_paediatric_assessment_in_acute_or_nonacute_setting partial, itself
    parent to single_choice_multiple_choice_toggle partial, whose button name stores the selected value
    On selection first_paediatric_assessment_in_acute_or_nonacute_setting partial is returned.
    """

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
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'has_number_of_episodes_since_the_first_been_documented', 'toggle_button')
def has_number_of_episodes_since_the_first_been_documented(request, first_paediatric_assessment_id):
    """
    POST request from toggle in has_number_of_episodes_since_the_first_been_documented partial
    """

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
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'general_examination_performed', 'toggle_button')
def general_examination_performed(request, first_paediatric_assessment_id):
    """
    POST request from toggle in has_general_examination_performed partial
    """

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
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'neurological_examination_performed', 'toggle_button')
def neurological_examination_performed(request, first_paediatric_assessment_id):
    """
    POST request from toggle in neurological_examination_performed partial
    """

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
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'developmental_learning_or_schooling_problems', 'toggle_button')
def developmental_learning_or_schooling_problems(request, first_paediatric_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """

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
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(FirstPaediatricAssessment, 'behavioural_or_emotional_problems', 'toggle_button')
def behavioural_or_emotional_problems(request, first_paediatric_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """

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
        context=context
    )

    return response
