from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants import *
from ..general_functions.value_from_key import value_from_key

from ..models import Registration
from ..models import InitialAssessment


@login_required
def initial_assessment(request, case_id):
    registration = Registration.objects.get(case=case_id)
    initial_assessment, created = InitialAssessment.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "initial_assessment": initial_assessment,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
        # "registration_complete": registration.audit_progress.registration_complete,
        # "initial_assessment_complete": registration.audit_progress.initial_assessment_complete,
        # "assessment_complete": registration.audit_progress.assessment_complete,
        # "epilepsy_context_complete": registration.audit_progress.epilepsy_context_complete,
        # "multiaxial_description_complete": registration.audit_progress.multiaxial_description_complete,
        # "investigation_complete": registration.audit_progress.investigation_complete,
        # "management_complete": registration.audit_progress.management_complete,
        "audit_progress": registration.audit_progress,
        "active_template": "initial_assessment"
    }

    return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


# htmx

def date_of_initial_assessment(request, initial_assessment_id):
    """
    HTMX call back from date_of_initial_assessment partial
    """
    date_of_initial_assessment = request.POST.get(request.htmx.trigger_name)
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

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment
    }

    return render(request=request, template_name='epilepsy12/partials/initial_assessment/date_of_initial_assessment.html', context=context)


def first_paediatric_assessment_in_acute_or_nonacute_setting(request, initial_assessment_id):
    """
    HTMX callback from first_paediatric_assessment_in_acute_or_nonacute_setting partial, itself
    parent to single_choice_multiple_choice_toggle partial, whose button name stores the selected value
    On selection first_paediatric_assessment_in_acute_or_nonacute_setting partial is returned.
    """

    first_paediatric_assessment_in_acute_or_nonacute_setting = int(
        request.htmx.trigger_name)
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(first_paediatric_assessment_in_acute_or_nonacute_setting=first_paediatric_assessment_in_acute_or_nonacute_setting)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "chronicity_selection": CHRONICITY,
        "initial_assessment": initial_assessment
    }

    return render(request=request, template_name="epilepsy12/partials/initial_assessment/first_paediatric_assessment_in_acute_or_nonacute_setting.html", context=context)


def general_paediatrics_referral_made(request, initial_assessment_id):
    """
    HTMX callback from general_paediatrics_referral_made_partial, itself the parent of a toggle_button 
    partial instance. The name of the post request toggles this field in the model and returns the 
    same partial.
    """

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    general_paediatrics_referral_made = not initial_assessment.general_paediatrics_referral_made

    if general_paediatrics_referral_made:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(general_paediatrics_referral_made=True)
    else:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(
                general_paediatrics_referral_made=False,
                date_of_referral_to_general_paediatrics=None
        )

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        'initial_assessment': initial_assessment
    }

    return render(request=request, template_name='epilepsy12/partials/initial_assessment/general_paediatrics_referral_made.html', context=context)


def date_of_referral_to_general_paediatrics(request, initial_assessment_id):
    """
    HTMX call back from date_of_initial_assessment partial
    """
    date_of_referral_to_general_paediatrics = request.POST.get(
        'date_of_referral_to_general_paediatrics')

    if date_of_referral_to_general_paediatrics:
        new_date = datetime.strptime(
            date_of_referral_to_general_paediatrics, "%Y-%m-%d").date()
        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                date_of_referral_to_general_paediatrics=new_date)
        except Exception as error:
            message = error

    else:
        message = "no dice"

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment
    }

    return render(request=request, template_name="epilepsy12/partials/initial_assessment/date_of_referral_to_general_paediatrics.html", context=context)


def when_the_first_epileptic_episode_occurred(request, initial_assessment_id):

    when_the_first_epileptic_episode_occurred = request.POST.get(
        'when_the_first_epileptic_episode_occurred')

    if when_the_first_epileptic_episode_occurred:
        new_date = datetime.strptime(
            when_the_first_epileptic_episode_occurred, "%Y-%m-%d").date()
        # TODO validation goes here

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred=new_date)
        except Exception as error:
            message = error

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        'initial_assessment_id': initial_assessment_id,
        'initial_assessment': initial_assessment,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }

    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def when_the_first_epileptic_episode_occurred_confidence(request, initial_assessment_id):
    """
    HTMX callback from when_the_first_epileptic_episode_occurred
    """
    when_the_first_epileptic_episode_occurred_confidence = request.htmx.trigger_name
    print(f"hello {when_the_first_epileptic_episode_occurred_confidence}")

    if when_the_first_epileptic_episode_occurred_confidence:
        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred_confidence=when_the_first_epileptic_episode_occurred_confidence)
        except Exception as error:
            message = error

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        'initial_assessment_id': initial_assessment_id,
        'initial_assessment': initial_assessment,
        "chronicity_selection": CHRONICITY,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }

    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def has_description_of_the_episode_or_episodes_been_gathered(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    has_description_of_the_episode_or_episodes_been_gathered = not initial_assessment.has_description_of_the_episode_or_episodes_been_gathered

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            has_description_of_the_episode_or_episodes_been_gathered=has_description_of_the_episode_or_episodes_been_gathered)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def has_number_of_episodes_since_the_first_been_documented(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    has_number_of_episodes_since_the_first_been_documented = not initial_assessment.has_number_of_episodes_since_the_first_been_documented

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            has_number_of_episodes_since_the_first_been_documented=has_number_of_episodes_since_the_first_been_documented)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def general_examination_performed(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    general_examination_performed = not initial_assessment.general_examination_performed

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            general_examination_performed=general_examination_performed)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def neurological_examination_performed(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    neurological_examination_performed = not initial_assessment.neurological_examination_performed

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            neurological_examination_performed=neurological_examination_performed)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def developmental_learning_or_schooling_problems(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    developmental_learning_or_schooling_problems = not initial_assessment.developmental_learning_or_schooling_problems

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            developmental_learning_or_schooling_problems=developmental_learning_or_schooling_problems)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def behavioural_or_emotional_problems(request, initial_assessment_id):

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)
    behavioural_or_emotional_problems = not initial_assessment.behavioural_or_emotional_problems

    try:
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            behavioural_or_emotional_problems=behavioural_or_emotional_problems)
    except Exception as error:
        return HttpResponse(error)

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


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

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)


def episode_definition(request, initial_assessment_id):

    episode_definition = request.POST.get(
        'episode_definition')
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(episode_definition=episode_definition)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment,
        "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        "episode_definition_selection": EPISODE_DEFINITION,
    }
    return render(request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)
