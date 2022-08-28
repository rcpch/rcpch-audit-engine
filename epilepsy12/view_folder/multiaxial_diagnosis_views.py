from django.utils import timezone
from datetime import datetime
from operator import itemgetter
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..constants import AUTOANTIBODIES, EPILEPSY_CAUSES, EPILEPSY_GENE_DEFECTS, EPILEPSY_GENETIC_CAUSE_TYPES, EPILEPSY_STRUCTURAL_CAUSE_TYPES, IMMUNE_CAUSES, METABOLIC_CAUSES, GENERALISED_SEIZURE_TYPE
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, EPIS_MISC, MIGRAINES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPTIC_SYNCOPES
from epilepsy12.constants.syndromes import SYNDROMES
from epilepsy12.constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from epilepsy12.models import episode
from epilepsy12.view_folder.initial_assessment_views import episode_definition
from ..constants import DATE_ACCURACY, EPISODE_DEFINITION
from django_htmx.http import trigger_client_event
from ..general_functions import fuzzy_scan_for_keywords

from ..models import Registration, Keyword, Episode, AuditProgress, Comorbidity, Episode

from ..general_functions import *

"""
Constants for selections
"""
FOCAL_EPILEPSY_FIELDS = [
    # "experienced_prolonged_focal_seizures",
    "focal_onset_impaired_awareness",
    "focal_onset_automatisms",
    "focal_onset_atonic",
    "focal_onset_clonic",
    "focal_onset_left",
    "focal_onset_right",
    "focal_onset_epileptic_spasms",
    "focal_onset_hyperkinetic",
    "focal_onset_myoclonic",
    "focal_onset_tonic",
    "focal_onset_autonomic",
    "focal_onset_behavioural_arrest",
    "focal_onset_cognitive",
    "focal_onset_emotional",
    "focal_onset_sensory",
    "focal_onset_centrotemporal",
    "focal_onset_temporal",
    "focal_onset_frontal",
    "focal_onset_parietal",
    "focal_onset_occipital",
    "focal_onset_gelastic",
    "focal_onset_focal_to_bilateral_tonic_clonic",
    # "focal_onset_other",
]

GENERALISED_ONSET_EPILEPSY_FIELDS = [
    # 'prolonged_generalized_convulsive_seizures',
    "epileptic_generalised_onset",
    # "epileptic_generalised_onset_other_details",
]

FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS = [
    {'name': 'focal_onset_atonic', 'text': "Atonic"},
    {'name': 'focal_onset_clonic', 'text': 'Clonic'},
    {'name': 'focal_onset_epileptic_spasms', 'text': 'Spasms'},
    {'name': 'focal_onset_hyperkinetic', 'text': 'Hyperkinetic'},
    {'name': 'focal_onset_myoclonic', 'text': 'Myoclonic'},
    {'name': 'focal_onset_tonic', 'text': 'Tonic'},
    {'name': 'focal_onset_focal_to_bilateral_tonic_clonic', 'text': 'Tonic-Clonic'},
]
FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS = [
    {'name': 'focal_onset_automatisms', 'text': 'Automatisms'},
    {'name': 'focal_onset_impaired_awareness', 'text': 'Impaired Awareness'},
    {'name': 'focal_onset_gelastic', 'text': 'Gelastic'},
    {'name': 'focal_onset_autonomic', 'text': 'Autonomic'},
    {'name': 'focal_onset_behavioural_arrest', 'text': 'Behavioural Arrest'},
    {'name': 'focal_onset_cognitive', 'text': 'Cognitive'},
    {'name': 'focal_onset_emotional', 'text': 'Emotional'},
    {'name': 'focal_onset_sensory', 'text': 'Sensory'}
]
FOCAL_EPILEPSY_EEG_MANIFESTATIONS = [
    {'name': 'focal_onset_centrotemporal', 'text': 'Centrotemporal'},
    {'name': 'focal_onset_temporal', 'text': 'Temporal'},
    {'name': 'focal_onset_frontal', 'text': 'Frontal'},
    {'name': 'focal_onset_parietal', 'text': 'Parietal'},
    {'name': 'focal_onset_occipital', 'text': 'Occipital'},
]
LATERALITY = [
    {'name': 'focal_onset_left', 'text': 'Left'},
    {'name': 'focal_onset_right', 'text': 'Right'}
]

EPILEPSY_FIELDS = ['were_any_of_the_epileptic_seizures_convulsive'] + \
    FOCAL_EPILEPSY_FIELDS + GENERALISED_ONSET_EPILEPSY_FIELDS


@login_required
def multiaxial_diagnosis(request, case_id):
    """
    """
    registration = Registration.objects.filter(case=case_id).get()
    """
    if Episode.objects.filter(registration=registration).exists():
        # there is already a desscribe object for this registration
        desscribe = Episode.objects.filter(registration=registration).first()
    else:
        # this is not yet a desscribe object for this description - create one
        desscribe = Episode.objects.create(registration=registration)
    """

    episodes = Episode.objects.filter(registration=registration).all()

    keyword_choices = Keyword.objects.all()

    # test_fields_update_audit_progress(desscribe)

    context = {
        "registration": registration,
        "episodes": episodes,
        "keyword_choices": keyword_choices,
        "case_id": case_id,
        "audit_progress": registration.audit_progress,
        "active_template": "multiaxial_diagnosis",
    }

    response = render(
        request=request, template_name='epilepsy12/multiaxial_diagnosis.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
def add_episode(request, registration_id):
    """
    HTMX post request from episodes.html partial on button click to add new episode
    """
    new_episode = Episode.objects.create(
        registration=Registration.objects.get(pk=registration_id),
        seizure_onset_date_confidence=None,
        has_description_of_the_episode_or_episodes_been_gathered=None,
        episode_definition=None,
        has_number_of_episodes_since_the_first_been_documented=None,
        description='',
        description_keywords=None,
        epilepsy_or_nonepilepsy_status=None
    )

    keywords = Keyword.objects.all()

    context = {
        'episode': new_episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/forms/episode_form.html', context)

    # test_fields_update_audit_progress(desscribe)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def edit_episode(request, episode_id):
    """
    HTMX post request from episodes.html partial on button click to add new episode
    """
    episode = Episode.objects.get(pk=episode_id)

    keywords = Keyword.objects.all()

    context = {
        'episode': episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords,
        'epilepsy_or_nonepilepsy_status_choices': sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'GENERALISED_SEIZURE_TYPE': sorted(GENERALISED_SEIZURE_TYPE, key=itemgetter(1)),
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
    }

    response = render(
        request, 'epilepsy12/forms/episode_form.html', context)

    # test_fields_update_audit_progress(desscribe)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def seizure_onset_date(request, episode_id):
    """
    HTMX post request from episode.html partial on date change
    """
    seizure_onset_date = request.POST.get(
        request.htmx.trigger_name)

    Episode.objects.filter(pk=episode_id).update(
        seizure_onset_date=datetime.strptime(
            seizure_onset_date, "%Y-%m-%d").date(),
        updated_at=timezone.now(),
        updated_by=request.user
    )

    episode = Episode.objects.get(pk=episode_id)

    keywords = Keyword.objects.all()

    context = {
        'episode': episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/episode.html', context)
    return response


@login_required
def seizure_onset_date_confidence(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    seizure_onset_date_confidence = request.htmx.trigger_name

    Episode.objects.filter(pk=episode_id).update(
        seizure_onset_date_confidence=seizure_onset_date_confidence,
        updated_at=timezone.now(),
        updated_by=request.user
    )

    episode = Episode.objects.get(pk=episode_id)

    keywords = Keyword.objects.all()

    context = {
        'episode': episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/episode.html', context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def definition(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    episode_definition = request.POST.get(request.htmx.trigger_name)

    Episode.objects.filter(pk=episode_id).update(
        episode_definition=episode_definition,
        updated_at=timezone.now(),
        updated_by=request.user
    )

    episode = Episode.objects.get(pk=episode_id)

    keywords = Keyword.objects.all()

    context = {
        'episode': episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/episode.html', context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def has_description_of_the_episode_or_episodes_been_gathered(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    if request.htmx.trigger_name == 'button-true':
        has_description_of_the_episode_or_episodes_been_gathered = True
    elif request.htmx.trigger_name == 'button-false':
        has_description_of_the_episode_or_episodes_been_gathered = False
    else:
        raise Exception

    keywords = Keyword.objects.all()

    Episode.objects.filter(pk=episode_id).update(
        has_description_of_the_episode_or_episodes_been_gathered=has_description_of_the_episode_or_episodes_been_gathered,
        description='',
        description_keywords=[],
        updated_at=timezone.now(),
        updated_by=request.user
    )

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        'seizure_onset_date_confidence_selection': DATE_ACCURACY,
        'episode_definition_selection': EPISODE_DEFINITION,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/episode.html', context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


"""
Description fields
"""


@login_required
def edit_description(request, episode_id):
    """
    This function is triggered by an htmx post request from the partials/episode/description.html form for the desscribe description.
    This component comprises the input free text describing a seizure episode and labels for each of the keywords identified.
    The htmx post request is triggered on every key up.
    This function returns the description keyword partial to the browser.
    TODO #33 implement 5000 character cut off
    """

    description = request.POST.get('description')

    keywords = Keyword.objects.all()
    matched_keywords = fuzzy_scan_for_keywords(description, keywords)

    update_field = {
        'description': description,
        'description_keywords': matched_keywords,
        'updated_at': timezone.now(),
        'updated_by': request.user
    }
    if (len(description) <= 5000):
        Episode.objects.update_or_create(
            pk=episode_id, defaults=update_field)
    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/description_labels.html', context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def delete_description_keyword(request, episode_id, description_keyword_id):
    """
    This function is triggered by an htmx post request from the partials/desscribe/description.html form for the desscribe description_keyword.
    This component comprises the input free text describing a seizure episode and labels for each of the keywords identified.
    The htmx post request is triggered on click of a keyword. It removes that keyword from the saved list.
    This function returns html to the browser.
    """
    description_keyword_list = Episode.objects.filter(
        pk=episode_id).values('description_keywords')
    description_keywords = description_keyword_list[0]['description_keywords']
    del description_keywords[description_keyword_id]

    Episode.objects.filter(pk=episode_id).update(
        description_keywords=description_keywords,
        updated_at=timezone.now(),
        updated_by=request.user)

    episode = Episode.objects.get(pk=episode_id)
    keywords = Keyword.objects.all()

    context = {
        'episode': episode,
        'keyword_selection': keywords
    }

    response = render(
        request, 'epilepsy12/partials/multiaxial_diagnosis/description_labels.html', context)

    # test_fields_update_audit_progress(desscribe)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


"""
Epilepsy status
"""


@login_required
def epilepsy_or_nonepilepsy_status(request, episode_id):
    """
    Function triggered by a click in the epilepsy_or_nonepilepsy_status partial leading to a post request.
    The episode_id is also passed in allowing update of the model.
    Selections for epilepsy set all nonepilepsy related fields to None, and selections for
    nonepilepsy set all epilepsy fields to None. Selections to not known set all 
    selections to none. The epilepsy_or_nonepilepsy_status partial is returned.
    """
    epilepsy_or_nonepilepsy_status = request.htmx.trigger_name

    # if epilepsy_or_nonepilepsy_status == 'E':
    #     # epilepsy selected - set all nonepilepsy to none
    #     set_epilepsy_fields_to_none(request, episode_id=episode_id)
    # elif epilepsy_or_nonepilepsy_status == 'NE':
    #     # nonepilepsy selected - set all epilepsy to none
    #     set_all_nonepilepsy_fields_to_none(request, episode_id=episode_id)
    # elif epilepsy_or_nonepilepsy_status == 'NK':
    #     # notknown selected - set all epilepsy and nonepilepsy to none
    #     set_epilepsy_fields_to_none(request, episode_id=episode_id)
    #     set_all_nonepilepsy_fields_to_none(request, episode_id=episode_id)

    Episode.objects.filter(pk=episode_id).update(
        epilepsy_or_nonepilepsy_status=epilepsy_or_nonepilepsy_status,
        updated_at=timezone.now(),
        updated_by=request.user
    )
    episode = Episode.objects.get(pk=episode_id)

    template = 'epilepsy12/partials/multiaxial_diagnosis/epilepsy_or_nonepilepsy_status.html'
    context = {
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        # 'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'GENERALISED_SEIZURE_TYPE': sorted(GENERALISED_SEIZURE_TYPE, key=itemgetter(1)),
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
        'episode': episode
    }

    response = render(request=request, template_name=template, context=context)

    # test_fields_update_audit_progress(desscribe)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def epilepsy_or_nonepilepsy_status(request, episode_id):
    """
    Function triggered by a click in the epilepsy_or_nonepilepsy_status partial leading to a post request.
    The episode_id is also passed in allowing update of the model.
    Selections for epilepsy set all nonepilepsy related fields to None, and selections for
    nonepilepsy set all epilepsy fields to None. Selections to not known set all 
    selections to none. The epilepsy_or_nonepilepsy_status partial is returned.
    """
    epilepsy_or_nonepilepsy_status = request.htmx.trigger_name
    """
    if epilepsy_or_nonepilepsy_status == 'E':
        # epilepsy selected - set all nonepilepsy to none
        set_epilepsy_fields_to_none(request, episode_id=episode_id)
    elif epilepsy_or_nonepilepsy_status == 'NE':
        # nonepilepsy selected - set all epilepsy to none
        set_all_nonepilepsy_fields_to_none(request, episode_id=episode_id)
    elif epilepsy_or_nonepilepsy_status == 'NK':
        # notknown selected - set all epilepsy and nonepilepsy to none
        set_epilepsy_fields_to_none(request, episode_id=episode_id)
        set_all_nonepilepsy_fields_to_none(request, episode_id=episode_id)
    """
    Episode.objects.filter(pk=episode_id).update(
        epilepsy_or_nonepilepsy_status=epilepsy_or_nonepilepsy_status,
        updated_at=timezone.now(),
        updated_by=request.user
    )
    episode = Episode.objects.get(pk=episode_id)

    template = 'epilepsy12/partials/multiaxial_diagnosis/epilepsy_or_nonepilepsy_status.html'
    context = {
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'GENERALISED_SEIZURE_TYPE': sorted(GENERALISED_SEIZURE_TYPE, key=itemgetter(1)),
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
        'episode': episode
    }

    response = render(request=request, template_name=template, context=context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


"""
Epilepsy fields
"""


@login_required
def were_any_of_the_epileptic_seizures_convulsive(request, episode_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    if request.htmx.trigger_name == 'button-true':
        were_any_of_the_epileptic_seizures_convulsive = True
    elif request.htmx.trigger_name == 'button-false':
        were_any_of_the_epileptic_seizures_convulsive = False
    else:
        were_any_of_the_epileptic_seizures_convulsive = None

    Episode.objects.filter(pk=episode_id).update(
        were_any_of_the_epileptic_seizures_convulsive=were_any_of_the_epileptic_seizures_convulsive,
        updated_at=timezone.now(),
        updated_by=request.user
    )

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
    }

    response = render(
        request=request, template_name='epilepsy12/partials/multiaxial_diagnosis/epilepsy.html', context=context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def epileptic_seizure_onset_type(request, episode_id):
    """
    Defines type of onset if considered to be epilepsy
    Accepts POST request from epilepsy partial and returns the same having
    updated the model with the selection
    If focal onset, sent general onset fields to none, or both 
    to none if not known
    """

    epileptic_seizure_onset_type = request.htmx.trigger_name

    update_fields = {}
    if epileptic_seizure_onset_type == "FO":
        # focal onset - set all generalised onset fields to none
        for field in GENERALISED_ONSET_EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })
    elif epileptic_seizure_onset_type == "GO":
        # generalised onset - set focal onset fields to none
        for field in FOCAL_EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })
    else:
        # unknown or unclassified onset. Set all to none
        for field in EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })

    # update the fields object to include latest selection
    update_fields.update({
        'epileptic_seizure_onset_type': epileptic_seizure_onset_type,
        'updated_at': timezone.now(),
        'updated_by': request.user
    })

    # update the model
    Episode.objects.filter(pk=episode_id).update(**update_fields)

    # retrieve updated object instance
    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        "GENERALISED_SEIZURE_TYPE": sorted(GENERALISED_SEIZURE_TYPE),
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
    }

    response = render(
        request=request, template_name='epilepsy12/partials/multiaxial_diagnosis/epilepsy.html', context=context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def focal_onset_epilepsy_checked_changed(request, episode_id):
    """
    Function triggered by a change in any checkbox/toggle in the focal_onset_epilepsy template leading to a post request.
    The episode_id is also passed in allowing update of the model.
    The id of the radio button clicked holds the name of the field in the desscribe model to update
    the name of the radiobutton group clicked holds the name of the list from which to select model fields to update
    """

    if request.htmx.trigger_name == 'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS':
        focal_fields = FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS
    elif request.htmx.trigger_name == 'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS':
        focal_fields = FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS
    elif request.htmx.trigger_name == 'FOCAL_EPILEPSY_EEG_MANIFESTATIONS':
        focal_fields = FOCAL_EPILEPSY_EEG_MANIFESTATIONS
    elif request.htmx.trigger_name == 'LATERALITY':
        focal_fields = LATERALITY
    else:
        # TODO this is an error that needs handling
        focal_fields = ()

    update_fields = {}
    for item in focal_fields:
        if request.htmx.trigger == item.get('name'):
            update_fields.update({
                item.get('name'): True
            })
        else:
            update_fields.update({
                item.get('name'): False
            })
    update_fields.update({
        'updated_at': timezone.now(),
        'updated_by': request.user
    })

    Episode.objects.filter(pk=episode_id).update(**update_fields)

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        'LATERALITY': LATERALITY,
        'FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS': FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        'FOCAL_EPILEPSY_EEG_MANIFESTATIONS': FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
    }

    response = render(
        request=request, template_name="epilepsy12/partials/multiaxial_diagnosis/focal_onset_epilepsy.html", context=context)

    # test_fields_update_audit_progress(episode)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


def epileptic_generalised_onset(request, episode_id):
    """
    POST request from epileptic_generalised_onset field in generalised_onset_epilepsy
    """
    epileptic_generalised_onset = request.POST.get(request.htmx.trigger_name)

    Episode.objects.filter(pk=episode_id).update(
        epileptic_generalised_onset=epileptic_generalised_onset
    )

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        "GENERALISED_SEIZURE_TYPE": sorted(GENERALISED_SEIZURE_TYPE),
    }

    template_name = 'epilepsy12/partials/multiaxial_diagnosis/generalised_onset_epilepsy.html'

    response = render(
        request=request, template_name=template_name, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response
