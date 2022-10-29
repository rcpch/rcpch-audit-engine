from django_htmx.http import trigger_client_event
from django.shortcuts import render
from django.db import IntegrityError

from epilepsy12.models.audit_progress import AuditProgress


def recalculate_form_generate_response(model_instance, request, context, template):
    """
    calculates form scores, creates response object and attaches htmx trigger
    """

    # calculate totals on form
    test_fields_update_audit_progress(model_instance)

    response = render(
        request=request, template_name=template, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response

# test all fields


def test_fields_update_audit_progress(model_instance):
    """
    Calculates all completed fields and compares expected fields
    Stores these values in AuditProgress
    Accepts model instance as parameter - uses this select correct fields to update
    """

    verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')

    all_completed_fields = completed_fields(model_instance)
    all_fields = total_fields_expected(model_instance)

    update_fields = {
        f'{verbose_name_underscored}_total_expected_fields': all_fields,
        f'{verbose_name_underscored}_total_completed_fields': all_completed_fields,
        f'{verbose_name_underscored}_complete': all_completed_fields == all_fields,
    }

    try:
        AuditProgress.objects.filter(
            registration=model_instance.registration).update(**update_fields)
    except IntegrityError as error:
        raise Exception(error)


def completed_fields(model_instance):
    """
    Test for all completed fields
    """
    fields = model_instance._meta.get_fields()
    counter = 0
    for field in fields:
        if (
                getattr(model_instance, field.name) is not None
                and field.name not in avoid_fields(model_instance)
        ):
            counter += 1
    return counter


def total_fields_expected(model_instance):
    """
    a minimum total fields would be:
    """

    cumulative_fields = scoreable_fields_for_model_instance(
        model_instance=model_instance)

    return len(cumulative_fields)


def avoid_fields(model_instance):
    """
    When looping through fields and counting them as complete/incomplete, these fields depending on the model
    should be avoided
    """
    verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')

    if verbose_name_underscored in ['first_paediatric_assessment', 'epilepsy_context', 'assessment', 'investigation']:
        return ['id', 'registration', 'updated_at', 'updated_by', 'created_at', 'created_by']
    if verbose_name_underscored == 'multiaxial_diagnosis':
        return ['id', 'registration', 'multiaxial_diagnosis', 'episode', 'syndrome', 'comorbidity', 'created_by', 'created_at', 'updated_by', 'updated_at']
    if verbose_name_underscored == 'multiaxial_diagnosis':
        return ['id', 'registration', 'multiaxial_diagnosis', 'episode', 'syndrome', 'comorbidity', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif verbose_name_underscored == 'management':
        return ['id', 'registration', 'antiepilepsymedicine', 'created_by', 'created_at', 'updated_by', 'updated_at']
    else:
        raise ValueError(
            f'{verbose_name_underscored} not found to return fields to avoid in form calculation.')


def scoreable_fields_for_model_instance(model_instance):
    """
    Returns the scoreable fields best on the model instance at the time
    """
    verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')

    if verbose_name_underscored == 'epilepsy_context':
        return ['previous_febrile_seizure', 'previous_acute_symptomatic_seizure', 'is_there_a_family_history_of_epilepsy', 'previous_neonatal_seizures', 'diagnosis_of_epilepsy_withdrawn', 'were_any_of_the_epileptic_seizures_convulsive', 'experienced_prolonged_generalized_convulsive_seizures', 'experienced_prolonged_focal_seizures']
    elif verbose_name_underscored == 'first_paediatric_assessment':
        return ['first_paediatric_assessment_in_acute_or_nonacute_setting', 'has_number_of_episodes_since_the_first_been_documented', 'general_examination_performed', 'neurological_examination_performed', 'developmental_learning_or_schooling_problems', 'behavioural_or_emotional_problems']
