from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
        "episode_definition_selection": EPISODE_DEFINITION,
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
            updated_at=timezone.now(),
            updated_by=request.user,
            date_of_initial_assessment=new_date)
    except Exception as error:
        print(error)
        return HttpResponse(error)

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment
    }

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name='epilepsy12/partials/initial_assessment/date_of_initial_assessment.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


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
            pk=initial_assessment_id).update(
                first_paediatric_assessment_in_acute_or_nonacute_setting=first_paediatric_assessment_in_acute_or_nonacute_setting,
                updated_at=timezone.now(),
                updated_by=request.user
        )
    except Exception as error:
        print(error)
        return HttpResponse(error)

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
            pk=initial_assessment_id).update(
                general_paediatrics_referral_made=True,
                updated_at=timezone.now(),
                updated_by=request.user
        )
    else:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(
                general_paediatrics_referral_made=False,
                date_of_referral_to_general_paediatrics=None,
                updated_at=timezone.now(),
                updated_by=request.user
        )

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        'initial_assessment': initial_assessment
    }

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name='epilepsy12/partials/initial_assessment/general_paediatrics_referral_made.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


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
                date_of_referral_to_general_paediatrics=new_date,
                updated_at=timezone.now(),
                updated_by=request.user
            )
        except Exception as error:
            message = error

    else:
        message = "no dice"

    initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": initial_assessment
    }

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/date_of_referral_to_general_paediatrics.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def when_the_first_epileptic_episode_occurred(request, initial_assessment_id):

    when_the_first_epileptic_episode_occurred = request.POST.get(
        'when_the_first_epileptic_episode_occurred')

    if when_the_first_epileptic_episode_occurred:
        new_date = datetime.strptime(
            when_the_first_epileptic_episode_occurred, "%Y-%m-%d").date()
        # TODO validation goes here

        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred=new_date,
                updated_at=timezone.now(),
                updated_by=request.user
            )
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

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def when_the_first_epileptic_episode_occurred_confidence(request, initial_assessment_id):
    """
    HTMX callback from when_the_first_epileptic_episode_occurred
    """
    when_the_first_epileptic_episode_occurred_confidence = request.htmx.trigger_name

    if when_the_first_epileptic_episode_occurred_confidence:
        try:
            InitialAssessment.objects.filter(pk=initial_assessment_id).update(
                when_the_first_epileptic_episode_occurred_confidence=when_the_first_epileptic_episode_occurred_confidence,
                updated_at=timezone.now(),
                updated_by=request.user
            )
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

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


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

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def has_number_of_episodes_since_the_first_been_documented(request, initial_assessment_id):
    """
    POST request from toggle in has_number_of_episodes_since_the_first_been_documented partial
    """
    if request.htmx.trigger_name == 'button-true':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            has_number_of_episodes_since_the_first_been_documented=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            has_number_of_episodes_since_the_first_been_documented=False,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        # "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/has_number_of_episodes_since_the_first_been_documented.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def general_examination_performed(request, initial_assessment_id):
    """
    POST request from toggle in has_general_examination_performed partial
    """
    if request.htmx.trigger_name == 'button-true':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            general_examination_performed=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            general_examination_performed=False,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        # "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/general_examination_performed.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def neurological_examination_performed(request, initial_assessment_id):
    """
    POST request from toggle in neurological_examination_performed partial
    """
    if request.htmx.trigger_name == 'button-true':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            neurological_examination_performed=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            neurological_examination_performed=False,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        # "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/neurological_examination_performed.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def developmental_learning_or_schooling_problems(request, initial_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """
    if request.htmx.trigger_name == 'button-true':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            developmental_learning_or_schooling_problems=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            developmental_learning_or_schooling_problems=False,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        # "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/developmental_learning_or_schooling_problems.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def behavioural_or_emotional_problems(request, initial_assessment_id):
    """
    POST request from toggle in developmental_learning_or_schooling_problems partial
    """
    if request.htmx.trigger_name == 'button-true':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            behavioural_or_emotional_problems=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        InitialAssessment.objects.filter(pk=initial_assessment_id).update(
            behavioural_or_emotional_problems=False,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    new_initial_assessment = InitialAssessment.objects.get(
        pk=initial_assessment_id)

    context = {
        "initial_assessment": new_initial_assessment,
        # "when_the_first_epileptic_episode_occurred_confidence_selection": DATE_ACCURACY,
        # "diagnostic_status_selection": DIAGNOSTIC_STATUS,
        # "episode_definition_selection": EPISODE_DEFINITION,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/behavioural_or_emotional_problems.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def diagnostic_status(request, initial_assessment_id):

    diagnostic_status = request.POST.get(
        'diagnostic_status')
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(
                diagnostic_status=diagnostic_status,
                updated_at=timezone.now(),
                updated_by=request.user
        )
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

    test_fields_update_audit_progress(initial_assessment)

    response = render(
        request=request, template_name="epilepsy12/partials/initial_assessment/when_the_first_epileptic_episode_occurred.html", context=context)

# trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def episode_definition(request, initial_assessment_id):

    episode_definition = request.POST.get(
        'episode_definition')
    # validation here TODO

    try:
        InitialAssessment.objects.filter(
            pk=initial_assessment_id).update(
                episode_definition=episode_definition,
                updated_at=timezone.now(),
                updated_by=request.user)
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

    test_fields_update_audit_progress(initial_assessment)

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
    date_of_initial_assessment
    general_paediatrics_referral_made
    date_of_referral_to_general_paediatrics
    first_paediatric_assessment_in_acute_or_nonacute_setting
    has_description_of_the_episode_or_episodes_been_gathered
    when_the_first_epileptic_episode_occurred_confidence
    when_the_first_epileptic_episode_occurred
    has_number_of_episodes_since_the_first_been_documented
    general_examination_performed
    neurological_examination_performed
    developmental_learning_or_schooling_problems
    behavioural_or_emotional_problems
    diagnostic_status
    episode_definition
    """
    fields = model_instance._meta.get_fields()
    counter = 0
    for field in fields:
        if (
            getattr(model_instance, field.name) is not None
            and field.name not in ['id', 'registration', 'created_at', 'updated_at', 'created_by', 'updated_by']
        ):
            print(field.name)
            counter += 1
    return counter


def total_fields_expected(model_instance):
    """
    a minimum total fields would be:

    date_of_initial_assessment
    general_paediatrics_referral_made
    date_of_referral_to_general_paediatrics
    first_paediatric_assessment_in_acute_or_nonacute_setting
    has_description_of_the_episode_or_episodes_been_gathered
    when_the_first_epileptic_episode_occurred_confidence
    when_the_first_epileptic_episode_occurred
    has_number_of_episodes_since_the_first_been_documented
    general_examination_performed
    neurological_examination_performed
    developmental_learning_or_schooling_problems
    behavioural_or_emotional_problems
    diagnostic_status
    episode_definition

    if general_paediatrics_referral_made then add an additional field for the date

    """

    cumulative_fields = 13
    if model_instance.date_of_referral_to_general_paediatrics:
        cumulative_fields += 1

    return cumulative_fields
