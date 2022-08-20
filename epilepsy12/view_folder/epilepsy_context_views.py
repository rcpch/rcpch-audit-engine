
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.common import OPT_OUT_UNCERTAIN
from epilepsy12.models.comorbidity import Comorbidity

from epilepsy12.models.registration import Registration
from ..models import EpilepsyContext


@login_required
def epilepsy_context(request, case_id):

    registration = Registration.objects.filter(case=case_id).first()
    comorbidities = Comorbidity.objects.filter(
        case=case_id).all()

    epilepsy_context, created = EpilepsyContext.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
        "registration_complete": registration.audit_progress.registration_complete,
        "initial_assessment_complete": registration.audit_progress.initial_assessment_complete,
        "assessment_complete": registration.audit_progress.assessment_complete,
        "epilepsy_context_complete": registration.audit_progress.epilepsy_context_complete,
        "multiaxial_description_complete": registration.audit_progress.multiaxial_description_complete,
        "investigation_management_complete": registration.audit_progress.investigation_management_complete,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }
    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)

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
            pk=epilepsy_context_id).update(previous_febrile_seizure=previous_febrile_seizure)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    return render(request=request, template_name="epilepsy12/partials/epilepsy_context/previous_febrile_seizure.html", context=context)


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
            pk=epilepsy_context_id).update(previous_acute_symptomatic_seizure=previous_acute_symptomatic_seizure)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    return render(request=request, template_name="epilepsy12/partials/epilepsy_context/previous_acute_symptomatic_seizure.html", context=context)


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
            pk=epilepsy_context_id).update(is_there_a_family_history_of_epilepsy=is_there_a_family_history_of_epilepsy)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    return render(request=request, template_name="epilepsy12/partials/epilepsy_context/is_there_a_family_history_of_epilepsy.html", context=context)


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
            pk=epilepsy_context_id).update(previous_neonatal_seizures=previous_neonatal_seizures)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    return render(request=request, template_name="epilepsy12/partials/epilepsy_context/previous_neonatal_seizures.html", context=context)


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
            diagnosis_of_epilepsy_withdrawn=diagnosis_of_epilepsy_withdrawn_status)
    except Exception as error:
        message = error

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context
    }

    return render(request=request, template_name="epilepsy12/partials/epilepsy_context/epilepsy_diagnosis_withdrawn.html", context=context)
