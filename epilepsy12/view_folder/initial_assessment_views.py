from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants import *

from ..models import Registration
from ..models import InitialAssessment


@login_required
def initial_assessment(request, case_id):
    registration = Registration.objects.get(case=case_id)
    initial_assessment, created = InitialAssessment.objects.get_or_create(
        registration=registration)

    print(created)

    if created:
        initial_assessment_object = created
        print(initial_assessment_object)
    else:
        initial_assessment_object = initial_assessment

    context = {
        "case_id": case_id,
        "registration": registration,
        "initial_assessment": initial_assessment_object,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "initial_assessment"
    }

    return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


# @login_required
# def create_initial_assessment(request, case_id):
#     form = InitialAssessmentForm(request.POST or None)
#     initial_assessment = InitialAssessment.objects.filter(
#         registration__case=case_id).first()

#     registration = Registration.objects.filter(case=case_id).first()
#     if request.method == "POST":
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.registration = registration
#             Registration.objects.filter(case=case_id).update(
#                 initial_assessment_complete=True)
#             messages.success(
#                 request, "You successfully added an initial assessment!")
#             obj.save()
#             return redirect('update_initial_assessment', case_id)
#         else:
#             print('not valid')

#     context = {
#         "form": form,
#         "case_id": case_id,
#         "registration": registration,
#         "initial_assessment": initial_assessment,
#         "initial_assessment_complete": registration.initial_assessment_complete,
#         "assessment_complete": registration.assessment_complete,
#         "epilepsy_context_complete": registration.epilepsy_context_complete,
#         "multiaxial_description_complete": registration.multiaxial_description_complete,
#         "investigation_management_complete": registration.investigation_management_complete,
#         "active_template": "initial_assessment"
#     }
#     return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


# @login_required
# def update_initial_assessment(request, case_id):
#     initial_assessment = InitialAssessment.objects.filter(
#         registration__case=case_id).first()
#     registration = Registration.objects.filter(case=case_id).first()
#     form = InitialAssessmentForm(instance=initial_assessment)

#     if request.method == "POST":
#         if ('delete') in request.POST:
#             Registration.objects.filter(case=case_id).update(
#                 initial_assessment_complete=False)
#             initial_assessment.delete()
#             messages.success(
#                 request, "You successfully deleted the initial assessment.")
#             return redirect('create_initial_assessment', case_id)
#         form = InitialAssessmentForm(request.POST, instance=initial_assessment)
#         if form.is_valid:
#             obj = form.save()
#             obj.save()
#             Registration.objects.filter(case=case_id).update(
#                 epilepsy_context_complete=True)
#             messages.success(
#                 request, "You successfully updated the initial assessment.")

#     context = {
#         "form": form,
#         "case_id": case_id,
#         "registration": registration,
#         "initial_assessement": initial_assessment,
#         "initial_assessment_complete": registration.initial_assessment_complete,
#         "assessment_complete": registration.assessment_complete,
#         "epilepsy_context_complete": registration.epilepsy_context_complete,
#         "multiaxial_description_complete": registration.multiaxial_description_complete,
#         "investigation_management_complete": registration.investigation_management_complete,
#         "active_template": "initial_assessment"
#     }

#     return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


# @login_required
# def delete_initial_assessment(request, id):
#     initial_assessment = get_object_or_404(InitialAssessmentForm, id=id)
#     initial_assessment.delete()
#     return redirect('cases')


# htmx

def date_of_initial_assessment(request, initial_assessment_id):

    date_of_initial_assessment = request.POST.get('date_of_initial_assessment')
    # validation here TODO

    new_date = datetime.strptime(
        date_of_initial_assessment, "%Y-%m-%d").date()

    # save date
    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            date_of_initial_assessment=new_date)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse('Success')


def first_paediatric_assessment_in_acute_or_nonacute_setting(request, initial_assessment_id):

    first_paediatric_assessment_in_acute_or_nonacute_setting = request.POST.get(
        'first_paediatric_assessment_in_acute_or_nonacute_setting')
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(first_paediatric_assessment_in_acute_or_nonacute_setting=first_paediatric_assessment_in_acute_or_nonacute_setting)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")


def general_paediatrics_referral_made(request, initial_assessment_id):

    general_paediatrics_referral_made = request.POST.get(
        'general_paediatrics_referral_made')

    if general_paediatrics_referral_made == 'on':
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(general_paediatrics_referral_made=True)
    else:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(general_paediatrics_referral_made=False, date_of_referral_to_general_paediatrics=None)

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        'initial_assessment_id': initial_assessment_id,
        'initial_assessment': initial_assessment
    }

    return render(request=request, template_name='epilepsy12/partials/general_paediatrics_referral_made.html', context=context)


def date_of_referral_to_general_paediatrics(request, initial_assessment_id):

    date_of_referral_to_general_paediatrics = request.POST.get(
        'date_of_referral_to_general_paediatrics')
    message = "success"

    if date_of_referral_to_general_paediatrics:
        new_date = datetime.strptime(
            date_of_referral_to_general_paediatrics, "%Y-%m-%d").date()

        # TODO validation goes here

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                date_of_referral_to_general_paediatrics=new_date)
        except Exception as error:
            message = error

    return HttpResponse(message)


def when_the_first_epileptic_episode_occurred(request, initial_assessment_id):

    when_the_first_epileptic_episode_occurred = request.POST.get(
        'when_the_first_epileptic_episode_occurred')

    message = "success"

    if when_the_first_epileptic_episode_occurred:
        new_date = datetime.strptime(
            when_the_first_epileptic_episode_occurred, "%Y-%m-%d").date()
        # TODO validation goes here

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred=new_date)
        except Exception as error:
            message = error

    return HttpResponse(message)


def when_the_first_epileptic_episode_occurred_confidence(request, initial_assessment_id):

    when_the_first_epileptic_episode_occurred_confidence = request.POST.get(
        'when_the_first_epileptic_episode_occurred_confidence')

    message = "success"

    if when_the_first_epileptic_episode_occurred_confidence:
        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred_confidence=when_the_first_epileptic_episode_occurred_confidence)
        except Exception as error:
            message = error

    return HttpResponse(message)


def has_description_of_the_episode_or_episodes_been_gathered(request, initial_assessment_id):

    has_description_of_the_episode_or_episodes_been_gathered = request.POST.get(
        'has_description_of_the_episode_or_episodes_been_gathered')

    message = "success"
    selected = False

    if has_description_of_the_episode_or_episodes_been_gathered:
        if has_description_of_the_episode_or_episodes_been_gathered == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                has_description_of_the_episode_or_episodes_been_gathered=selected)
        except Exception as error:
            message = error

    print(selected)

    return HttpResponse(message)


def has_number_of_episodes_since_the_first_been_documented(request, initial_assessment_id):

    has_number_of_episodes_since_the_first_been_documented = request.POST.get(
        'has_number_of_episodes_since_the_first_been_documented')

    message = "success"
    selected = False

    if has_number_of_episodes_since_the_first_been_documented:
        if has_number_of_episodes_since_the_first_been_documented == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                has_number_of_episodes_since_the_first_been_documented=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)


def general_examination_performed(request, initial_assessment_id):

    general_examination_performed = request.POST.get(
        'general_examination_performed')

    message = "success"
    selected = False

    if general_examination_performed:
        if general_examination_performed == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                general_examination_performed=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)


def neurological_examination_performed(request, initial_assessment_id):

    neurological_examination_performed = request.POST.get(
        'neurological_examination_performed')

    message = "success"
    selected = False

    if neurological_examination_performed:
        if neurological_examination_performed == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                neurological_examination_performed=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)


def developmental_learning_or_schooling_problems(request, initial_assessment_id):

    developmental_learning_or_schooling_problems = request.POST.get(
        'developmental_learning_or_schooling_problems')

    message = "success"
    selected = False

    if developmental_learning_or_schooling_problems:
        if developmental_learning_or_schooling_problems == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                developmental_learning_or_schooling_problems=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)


def behavioural_or_emotional_problems(request, initial_assessment_id):

    behavioural_or_emotional_problems = request.POST.get(
        'behavioural_or_emotional_problems')

    message = "success"
    selected = False

    if behavioural_or_emotional_problems:
        if behavioural_or_emotional_problems == 'on':
            selected = True
        else:
            selected = False

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                behavioural_or_emotional_problems=selected)
        except Exception as error:
            message = error

    return HttpResponse(message)


def diagnostic_status(request, initial_assessment_id):

    diagnostic_status = request.POST.get(
        'diagnostic_status')
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(diagnostic_status=diagnostic_status)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    return HttpResponse("success")
