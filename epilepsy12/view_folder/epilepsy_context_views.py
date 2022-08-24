
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.common import OPT_OUT_UNCERTAIN
from epilepsy12.models.comorbidity import Comorbidity
from epilepsy12.models.registration import Registration
from ..models import EpilepsyContext
from epilepsy12.models.audit_progress import AuditProgress
from django_htmx.http import trigger_client_event


@login_required
def epilepsy_context(request, case_id):

    registration = Registration.objects.filter(case=case_id).first()
    comorbidities = Comorbidity.objects.filter(
        case=case_id).all()

    epilepsy_context, created = EpilepsyContext.objects.get_or_create(
        registration=registration)

    test_fields_update_audit_progress(epilepsy_context)

    context = {
        "case_id": case_id,
        "registration": registration,
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
        "audit_progress": epilepsy_context.registration.audit_progress,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }

    response = render(
        request=request, template_name='epilepsy12/epilepsy_context.html', context=context)
    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response

# HTMX


def previous_febrile_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    previous_febrile_seizure = request.htmx.trigger_name
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(
                previous_febrile_seizure=previous_febrile_seizure,
                updated_at=timezone.now(),
                updated_by=request.user)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    test_fields_update_audit_progress(epilepsy_context)

    response = render(
        request=request, template_name="epilepsy12/partials/epilepsy_context/previous_febrile_seizure.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def previous_acute_symptomatic_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    previous_acute_symptomatic_seizure = request.htmx.trigger_name
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(
                previous_acute_symptomatic_seizure=previous_acute_symptomatic_seizure,
                updated_at=timezone.now(),
                updated_by=request.user)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    test_fields_update_audit_progress(epilepsy_context)

    response = render(
        request=request, template_name="epilepsy12/partials/epilepsy_context/previous_acute_symptomatic_seizure.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def is_there_a_family_history_of_epilepsy(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    is_there_a_family_history_of_epilepsy = request.htmx.trigger_name
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(
                is_there_a_family_history_of_epilepsy=is_there_a_family_history_of_epilepsy,
                updated_at=timezone.now(),
                updated_by=request.user)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    test_fields_update_audit_progress(epilepsy_context)

    response = render(
        request=request, template_name="epilepsy12/partials/epilepsy_context/is_there_a_family_history_of_epilepsy.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def previous_neonatal_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    previous_neonatal_seizures = request.htmx.trigger_name
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(
                previous_neonatal_seizures=previous_neonatal_seizures,
                updated_at=timezone.now(),
                updated_by=request.user)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    test_fields_update_audit_progress(epilepsy_context)

    response = render(
        request=request, template_name="epilepsy12/partials/epilepsy_context/previous_neonatal_seizures.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def diagnosis_of_epilepsy_withdrawn(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)
    diagnosis_of_epilepsy_withdrawn_status = not epilepsy_context.diagnosis_of_epilepsy_withdrawn

    try:
        EpilepsyContext.objects.filter(pk=epilepsy_context_id).update(
            diagnosis_of_epilepsy_withdrawn=diagnosis_of_epilepsy_withdrawn_status,
            updated_at=timezone.now(),
            updated_by=request.user)
    except Exception as error:
        message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context
    }

    test_fields_update_audit_progress(epilepsy_context)

    response = render(
        request=request, template_name="epilepsy12/partials/epilepsy_context/epilepsy_diagnosis_withdrawn.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


# test all fields
def test_fields_update_audit_progress(model_instance):
    all_completed_fields = completed_fields(model_instance)
    all_fields = total_fields_expected(model_instance)

    AuditProgress.objects.filter(registration=model_instance.registration).update(
        epilepsy_context_total_expected_fields=all_fields,
        epilepsy_context_total_completed_fields=all_completed_fields,
        epilepsy_context_complete=all_completed_fields == all_fields
    )


def completed_fields(model_instance):
    """
    Test for all these completed fields
    previous_febrile_seizure
    previous_acute_symptomatic_seizure
    is_there_a_family_history_of_epilepsy
    previous_neonatal_seizures
    diagnosis_of_epilepsy_withdrawn
    """
    fields = model_instance._meta.get_fields()
    counter = 0
    for field in fields:
        if getattr(model_instance, field.name) is not None and field.name != 'id' and field.name != 'registration':
            counter += 1
    return counter


def total_fields_expected(model_instance):
    """
    a minimum total fields would be:

    previous_febrile_seizure
    previous_acute_symptomatic_seizure
    is_there_a_family_history_of_epilepsy
    previous_neonatal_seizures
    diagnosis_of_epilepsy_withdrawn

    """

    cumulative_fields = 5

    return cumulative_fields
