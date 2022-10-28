from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..decorator import group_required, update_model
from epilepsy12.constants import *
from epilepsy12.models.audit_progress import AuditProgress
from django_htmx.http import trigger_client_event

from ..models import Registration
from ..models import InitialAssessment


@login_required
def initial_assessment(request, case_id):
    registration = Registration.objects.get(case=case_id)

    if InitialAssessment.objects.filter(registration=registration).exists():
        initial_assessment = InitialAssessment.objects.filter(
            registration=registration).get()
    else:
        InitialAssessment.objects.create(
            registration=registration
            # will autoupdate date and user on creation
        )
        initial_assessment = InitialAssessment.objects.filter(
            registration=registration).get()

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "case_id": case_id,
        "registration": registration,
        "initial_assessment": initial_assessment,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "audit_progress": registration.audit_progress,
        "active_template": "initial_assessment"
    }

    response = render(
        request=request, template_name='epilepsy12/initial_assessment.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'first_paediatric_assessment_in_acute_or_nonacute_setting', 'multiple_choice_multiple_toggle_button')
def first_paediatric_assessment_in_acute_or_nonacute_setting(request, initial_assessment_id):
    """
    HTMX callback from first_paediatric_assessment_in_acute_or_nonacute_setting partial, itself
    parent to single_choice_multiple_choice_toggle partial, whose button name stores the selected value
    On selection first_paediatric_assessment_in_acute_or_nonacute_setting partial is returned.
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "chronicity_selection": CHRONICITY,
        "initial_assessment": initial_assessment
    }

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/first_paediatric_assessment_in_acute_or_nonacute_setting.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'has_number_of_episodes_since_the_first_been_documented', 'toggle_button')
def has_number_of_episodes_since_the_first_been_documented(request, initial_assessment_id):
    """
    POST request from toggle in has_number_of_episodes_since_the_first_been_documented partial
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "initial_assessment": initial_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'general_examination_performed', 'toggle_button')
def general_examination_performed(request, initial_assessment_id):
    """
    POST request from toggle in has_general_examination_performed partial
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "initial_assessment": initial_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'neurological_examination_performed', 'toggle_button')
def neurological_examination_performed(request, initial_assessment_id):
    """
    POST request from toggle in neurological_examination_performed partial
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "initial_assessment": initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'developmental_learning_or_schooling_problems', 'toggle_button')
def developmental_learning_or_schooling_problems(request, initial_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "initial_assessment": initial_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(InitialAssessment, 'behavioural_or_emotional_problems', 'toggle_button')
def behavioural_or_emotional_problems(request, initial_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    test_fields_update_audit_progress(initial_assessment)

    context = {
        "initial_assessment": initial_assessment,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def test_fields_update_audit_progress(model_instance):
    all_completed_fields = completed_fields(model_instance)
    all_fields = total_fields_expected(model_instance)

    AuditProgress.objects.filter(registration=model_instance.registration).update(
        initial_assessment_total_expected_fields=all_fields,
        initial_assessment_total_completed_fields=all_completed_fields,
        initial_assessment_complete=all_completed_fields == all_fields
    )


def completed_fields(model_instance):
    """
    Test for all these completed fields
    date_of_initial_assessment - DEPRECATED: MOVED TO REGISTRATION
    general_paediatrics_referral_made - DEPRECATED: MOVED TO ASSESSMENTS
    date_of_referral_to_general_paediatrics - DEPRECATED: MOVED TO ASSESSMENTS
    first_paediatric_assessment_in_acute_or_nonacute_setting
    has_description_of_the_episode_or_episodes_been_gathered - DEPRECATED: MOVED TO EPISODES
    when_the_first_epileptic_episode_occurred_confidence - DEPRECATED: MOVED TO EPISODES
    when_the_first_epileptic_episode_occurred - DEPRECATED - MOVED TO EPISODES
    has_number_of_episodes_since_the_first_been_documented
    general_examination_performed
    neurological_examination_performed
    developmental_learning_or_schooling_problems
    behavioural_or_emotional_problems
    diagnostic_status - DEPRECATED #138
    """
    fields = model_instance._meta.get_fields()
    counter = 0
    for field in fields:
        if (
            getattr(model_instance, field.name) is not None
            and field.name not in ['id', 'registration', 'created_at', 'updated_at', 'created_by', 'updated_by']
        ):
            counter += 1
    return counter


def total_fields_expected(model_instance):
    """
    a minimum total fields would be:

    date_of_initial_assessment - DEPRECATED: MOVED TO REGISTRATION
    general_paediatrics_referral_made - DEPRECATED: MOVED TO ASSESSMENTS
    date_of_referral_to_general_paediatrics - DEPRECATED: MOVED TO ASSESSMENTS
    first_paediatric_assessment_in_acute_or_nonacute_setting
    has_number_of_episodes_since_the_first_been_documented
    general_examination_performed
    neurological_examination_performed
    developmental_learning_or_schooling_problems
    behavioural_or_emotional_problems
    diagnostic_status - DEPRECATED #138

    if general_paediatrics_referral_made then add an additional field for the date - DEPRECATED

    """

    cumulative_fields = 6
    # if model_instance.date_of_referral_to_general_paediatrics:
    #     cumulative_fields += 1

    return cumulative_fields
