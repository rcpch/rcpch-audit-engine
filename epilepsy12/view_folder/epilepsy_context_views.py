
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
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }
    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)

# HTMX


def previous_febrile_seizure(request, epilepsy_context_id):

    previous_febrile_seizure = request.POST.get(
        'previous_febrile_seizure')
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(previous_febrile_seizure=previous_febrile_seizure)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")


def previous_acute_symptomatic_seizure(request, epilepsy_context_id):

    previous_acute_symptomatic_seizure = request.POST.get(
        'previous_acute_symptomatic_seizure')
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(previous_acute_symptomatic_seizure=previous_acute_symptomatic_seizure)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")


def is_there_a_family_history_of_epilepsy(request, epilepsy_context_id):

    is_there_a_family_history_of_epilepsy = request.POST.get(
        'is_there_a_family_history_of_epilepsy')
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(is_there_a_family_history_of_epilepsy=is_there_a_family_history_of_epilepsy)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")


def previous_neonatal_seizures(request, epilepsy_context_id):

    previous_neonatal_seizures = request.POST.get(
        'previous_neonatal_seizures')
    # validation here TODO

    try:
        EpilepsyContext.objects.filter(
            pk=epilepsy_context_id).update(previous_neonatal_seizures=previous_neonatal_seizures)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")


def diagnosis_of_epilepsy_withdrawn(request, epilepsy_context_id):

    diagnosis_of_epilepsy_withdrawn = request.POST.get(
        'diagnosis_of_epilepsy_withdrawn')

    message = "success"
    selected = False

    if diagnosis_of_epilepsy_withdrawn:
        if diagnosis_of_epilepsy_withdrawn == 'on':
            selected = True
        else:
            selected = False

        try:
            EpilepsyContext.objects.filter(pk=epilepsy_context_id).update(
                diagnosis_of_epilepsy_withdrawn=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)
