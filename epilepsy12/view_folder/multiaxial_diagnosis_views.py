from django.utils import timezone
from operator import itemgetter
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from epilepsy12.constants.comorbidities import NEUROPSYCHIATRIC
from ..decorator import group_required

from ..constants import EPILEPSY_CAUSES, GENERALISED_SEIZURE_TYPE
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, EPIS_MISC, MIGRAINES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPTIC_SYNCOPES
from epilepsy12.constants.syndromes import SYNDROMES
from epilepsy12.constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from ..constants import DATE_ACCURACY, EPISODE_DEFINITION
from ..general_functions import fuzzy_scan_for_keywords, fetch_ecl

from ..models import Registration, Keyword, Comorbidity, Episode, Syndrome, MultiaxialDiagnosis
from ..common_view_functions import validate_and_update_model, recalculate_form_generate_response

"""
Constants for selections
"""

# fields for radio buttons

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

nonseizure_types = [
    {'name': 'nonepileptic_seizure_syncope',
        'text': 'Syncope And Anoxic Seizures', 'id': 'SAS'},
    {'name': 'nonepileptic_seizure_behavioural',
        'text': 'Behavioral Psychological And Psychiatric Disorders', 'id': 'BPP'},
    {'name': 'nonepileptic_seizure_sleep',
        'text': 'Sleep Related Conditions', 'id': 'SRC'},
    {'name': 'nonepileptic_seizure_paroxysmal',
        'text': 'Paroxysmal Movement Disorders', 'id': 'PMD'},
    {'name': 'nonepileptic_seizure_migraine',
        'text': 'Migraine Associated Disorders', 'id': 'MAD'},
    {'name': 'nonepileptic_seizure_miscellaneous',
        'text': 'Miscellaneous Events', 'id': 'ME'},
    {'name': 'nonepileptic_seizure_other', 'text': 'Other', 'id': 'Oth'}
]

# fields to update in model

GENERALISED_ONSET_EPILEPSY_FIELDS = [
    "epileptic_generalised_onset",
]

FOCAL_EPILEPSY_FIELDS = [
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
]

EPILEPSY_FIELDS = ['epileptic_seizure_onset_type'] + \
    FOCAL_EPILEPSY_FIELDS + GENERALISED_ONSET_EPILEPSY_FIELDS

NONEPILEPSY_FIELDS = [
    'nonepileptic_seizure_unknown_onset',
    'nonepileptic_seizure_syncope',
    'nonepileptic_seizure_behavioural',
    'nonepileptic_seizure_sleep',
    'nonepileptic_seizure_paroxysmal',
    'nonepileptic_seizure_migraine',
    'nonepileptic_seizure_miscellaneous',
    'nonepileptic_seizure_other'
]

ALL_FIELDS = NONEPILEPSY_FIELDS + EPILEPSY_FIELDS


@login_required
def multiaxial_diagnosis(request, case_id):
    """
    Called on load of form. If no instance exists, one is created.

    """
    registration = Registration.objects.filter(case=case_id).get()
    if MultiaxialDiagnosis.objects.filter(registration=registration).exists():
        multiaxial_diagnosis = MultiaxialDiagnosis.objects.filter(
            registration=registration).get()
    else:
        MultiaxialDiagnosis.objects.update_or_create(
            registration=registration
        )
        multiaxial_diagnosis = MultiaxialDiagnosis.objects.filter(
            registration=registration).get()

    episodes = Episode.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('seizure_onset_date').all()

    there_are_epileptic_episodes = Episode.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis,
        epilepsy_or_nonepilepsy_status='E'
    ).exists()

    syndromes = Syndrome.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).all()

    comorbidities = Comorbidity.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).all()

    keyword_choices = Keyword.objects.all()

    ecl = '<< 363235000 '
    epilepsy_causes = fetch_ecl(ecl)

    context = {
        "case_id": registration.case_id,
        "registration": registration,
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "episodes": episodes,
        "syndromes": syndromes,
        'comorbidities': comorbidities,
        "keyword_choices": keyword_choices,
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
        'epilepsy_causes': sorted(epilepsy_causes, key=itemgetter('preferredTerm')),
        "case_id": case_id,
        "audit_progress": registration.audit_progress,
        "active_template": "multiaxial_diagnosis",
        'there_are_epileptic_episodes': there_are_epileptic_episodes,
        "mental_health_issues_choices": NEUROPSYCHIATRIC,
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/multiaxial_diagnosis.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def add_episode(request, multiaxial_diagnosis_id):
    """
    HTMX post request from episodes.html partial on button click to add new episode
    """
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    new_episode = Episode.objects.create(
        multiaxial_diagnosis=multiaxial_diagnosis,
        seizure_onset_date_confidence=None,
        has_description_of_the_episode_or_episodes_been_gathered=None,
        episode_definition=None,
        description='',
        description_keywords=None,
        epilepsy_or_nonepilepsy_status=None,
        epileptic_seizure_onset_type=None,
        nonepileptic_seizure_type=None,
        epileptic_generalised_onset=None,
        focal_onset_impaired_awareness=None,
        focal_onset_automatisms=None,
        focal_onset_atonic=None,
        focal_onset_clonic=None,
        focal_onset_left=None,
        focal_onset_right=None,
        focal_onset_epileptic_spasms=None,
        focal_onset_hyperkinetic=None,
        focal_onset_myoclonic=None,
        focal_onset_tonic=None,
        focal_onset_autonomic=None,
        focal_onset_behavioural_arrest=None,
        focal_onset_cognitive=None,
        focal_onset_emotional=None,
        focal_onset_sensory=None,
        focal_onset_centrotemporal=None,
        focal_onset_temporal=None,
        focal_onset_frontal=None,
        focal_onset_parietal=None,
        focal_onset_occipital=None,
        focal_onset_gelastic=None,
        focal_onset_focal_to_bilateral_tonic_clonic=None,
        nonepileptic_seizure_unknown_onset=None,
        nonepileptic_seizure_syncope=None,
        nonepileptic_seizure_behavioural=None,
        nonepileptic_seizure_sleep=None,
        nonepileptic_seizure_paroxysmal=None,
        nonepileptic_seizure_migraine=None,
        nonepileptic_seizure_miscellaneous=None,
        nonepileptic_seizure_other=None,
    )

    keywords = Keyword.objects.all()

    context = {
        'episode': new_episode,
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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
    }

    response = recalculate_form_generate_response(
        model_instance=new_episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),

        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_full_access', 'trust_audit_team_full_access')
def remove_episode(request, episode_id):
    """
    POST request on button click from episodes partial in multiaxial_diagnosis form
    Deletes episode from table
    """
    episode = Episode.objects.get(pk=episode_id)
    multiaxial_diagnosis = episode.multiaxial_diagnosis
    Episode.objects.get(pk=episode_id).delete()
    episodes = Episode.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('seizure_onset_date')

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'episodes': episodes
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episodes.html',
        context=context
    )

    return response


@login_required
def close_episode(request, episode_id):
    """
    Call back from onclick of close episode in episode.html
    returns the episodes list partial
    """
    episode = Episode.objects.get(
        pk=episode_id)
    multiaxial_diagnosis = episode.multiaxial_diagnosis

    # if all the fields are none this was not completed - delete the record
    if completed_fields(episode) == 0:
        episode.delete()

    episodes = Episode.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('seizure_onset_date')

    there_are_epileptic_episodes = Episode.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis,
        epilepsy_or_nonepilepsy_status='E'
    ).exists()

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'episodes': episodes,
        'there_are_epileptic_episodes': there_are_epileptic_episodes
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episodes.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def seizure_onset_date(request, episode_id):
    """
    HTMX post request from episode.html partial on date change
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='seizure_onset_date',
            page_element='date_field'
        )
    except ValueError as error:
        error_message = error

    keywords = Keyword.objects.all()
    episode = Episode.objects.get(pk=episode_id)

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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def seizure_onset_date_confidence(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='seizure_onset_date_confidence',
            page_element='single_choice_multiple_toggle_button'
        )
    except ValueError as error:
        error_message = error

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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),

        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def episode_definition(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='episode_definition',
            page_element='select'
        )
    except ValueError as error:
        error_message = error

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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_description_of_the_episode_or_episodes_been_gathered(request, episode_id):
    """
    HTMX post request from episode.html partial on toggle click
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='has_description_of_the_episode_or_episodes_been_gathered',
            page_element='toggle_button'
        )
    except ValueError as error:
        error_message = error

    keywords = Keyword.objects.all()

    episode = Episode.objects.get(pk=episode_id)

    # clean up
    if not episode.has_description_of_the_episode_or_episodes_been_gathered:
        # no description gathered - remove any previously gathered descriptions
        episode.description = ''
        episode.description_keywords = None
        episode.save()

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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/episode.html',
        context=context,
        error_message=error_message
    )

    return response


"""
Description fields
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
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

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/description_labels.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
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

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/description_labels.html',
        context=context
    )

    return response


"""
Epilepsy status
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def epilepsy_or_nonepilepsy_status(request, episode_id):
    """
    Function triggered by a click in the epilepsy_or_nonepilepsy_status partial leading to a post request.
    The episode_id is also passed in allowing update of the model.
    Selections for epilepsy set all nonepilepsy related fields to None, and selections for
    nonepilepsy set all epilepsy fields to None. Selections to not known set all
    selections to none. The epilepsy_or_nonepilepsy_status partial is returned.
    """
    epilepsy_or_nonepilepsy_status = request.htmx.trigger_name

    update_fields = {
        'epilepsy_or_nonepilepsy_status': epilepsy_or_nonepilepsy_status,
        'updated_at': timezone.now(),
        'updated_by': request.user,
    }

    if epilepsy_or_nonepilepsy_status == 'E':
        # epilepsy selected - set all nonepilepsy to none
        for field in NONEPILEPSY_FIELDS:
            update_fields.update({
                f"{field}": None
            })
    elif epilepsy_or_nonepilepsy_status == 'NE':
        # nonepilepsy selected - set all epilepsy to none
        for field in EPILEPSY_FIELDS:
            update_fields.update({
                f"{field}": None
            })
    elif epilepsy_or_nonepilepsy_status == 'U':
        # notknown selected - set all epilepsy and nonepilepsy to none
        for field in ALL_FIELDS:
            update_fields.update({
                f"{field}": None
            })

    Episode.objects.filter(pk=episode_id).update(**update_fields)
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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        'episode': episode
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template=template,
        context=context
    )

    return response


"""
Epilepsy fields
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
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
                f"{field}": None
            })
    elif epileptic_seizure_onset_type == "GO":
        # generalised onset - set focal onset fields to none
        for field in FOCAL_EPILEPSY_FIELDS:
            update_fields.update({
                f"{field}": None
            })
    else:
        # unknown or unclassified onset. Set all to none
        for field in EPILEPSY_FIELDS:
            update_fields.update({
                f"{field}": None
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

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/epilepsy.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def focal_onset_epilepsy_checked_changed(request, episode_id):
    """
    Function triggered by a change in any checkbox/toggle in the focal_onset_epilepsy template leading to a post request.
    The episode_id is also passed in allowing update of the model.
    The id of the radio button/checkbox clicked holds the name of the field in the desscribe model to update
    the name of the radiobutton/checkbox group clicked holds the name of the list from which to select model fields to update
    Laterality choices are radiobuttons (as can be either left or right, not both)
    All other choices are checkboxes and multiselect is enabled here
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

    episode = Episode.objects.get(pk=episode_id)

    update_fields = {}
    for item in focal_fields:
        item_status = getattr(episode, item.get('name'))
        if request.htmx.trigger == item.get('name'):
            # selects or deselects the chosen option - allows user to reverse previous selection
            update_fields.update({
                item.get('name'): not item_status
            })
        else:
            if request.htmx.trigger_name == 'LATERALITY':
                # sets the opposite side to that selected as false
                update_fields.update({
                    item.get('name'): False
                })
            else:
                # leaves all other selections the same - allows therefore multiselect
                update_fields.update({
                    item.get('name'): item_status
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

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template="epilepsy12/partials/multiaxial_diagnosis/focal_onset_epilepsy.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def epileptic_generalised_onset(request, episode_id):
    """
    POST request from epileptic_generalised_onset field in generalised_onset_epilepsy
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='epileptic_generalised_onset',
            page_element='select'
        )
    except ValueError as error:
        error_message = error

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'episode': episode,
        "GENERALISED_SEIZURE_TYPE": sorted(GENERALISED_SEIZURE_TYPE),
    }

    template_name = 'epilepsy12/partials/multiaxial_diagnosis/generalised_onset_epilepsy.html'

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template=template_name,
        context=context,
        error_message=error_message
    )

    return response


"""
Nonepilepsy
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def nonepilepsy_generalised_onset(request, episode_id):
    """
    POST request from toggle
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name='nonepileptic_seizure_unknown_onset',
            page_element='multiple_choice_multiple_toggle_button'
        )
    except ValueError as error:
        error_message = error

    episode = Episode.objects.get(id=episode_id)

    context = {
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        'episode': episode
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/nonepilepsy.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def nonepileptic_seizure_type(request, episode_id):
    """
    POST request from select element within nonepilepsy partial
    Returns one of the select options:
    nonepileptic_seizure_type
    nonepileptic_seizure_syncope
    nonepileptic_seizure_behavioural
    nonepileptic_seizure_sleep
    nonepileptic_seizure_paroxysmal
    nonepileptic_seizure_migraine
    nonepileptic_seizure_miscellaneous

    Updates the nonepileptic_seizure_type and used to filter which subtype is shown
    Returns the same partial with parameters
    """

    update_fields = {
        'nonepileptic_seizure_type': request.POST.get(request.htmx.trigger_name),
        'updated_at': timezone.now(),
        'updated_by': request.user
    }

    # set any fields that are not this subtype that might have previously been
    # set back to none
    for nonseizure_type in nonseizure_types:
        if nonseizure_type.get('id') is not nonepileptic_seizure_type:
            update_fields.update({
                nonseizure_type.get('name'): None
            })

    Episode.objects.filter(pk=episode_id).update(
        **update_fields
    )

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        'episode': episode
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/nonepilepsy.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def nonepileptic_seizure_subtype(request, episode_id):
    """
    POST request from the nonepileptic_seizure_subtype partial select component
    in the nonepilepsy partial
    Returns selection from one of the dropdowns depending on which nonepileptic_seizure_type
    was previously selected
    """
    field_name = request.htmx.trigger_name
    field_selection = request.POST.get(field_name)

    # set selected field to selection, all other nonepilepsy fields to None
    update_fields = {
        'updated_at': timezone.now(),
        'updated_by': request.user
    }
    for nonseizure_type in nonseizure_types:
        if nonseizure_type.get('name') == field_name:
            update_fields.update({
                field_name: field_selection
            })
        else:
            update_fields.update({
                nonseizure_type.get('name'): None
            })
    Episode.objects.filter(pk=episode_id).update(**update_fields)

    episode = Episode.objects.get(pk=episode_id)

    context = {
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
        'episode': episode
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/nonepilepsy.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def add_syndrome(request, multiaxial_diagnosis_id):
    """
    HTMX post request from syndromes.html partial on button click to add new syndrome
    """

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    syndrome = Syndrome.objects.create(
        multiaxial_diagnosis=multiaxial_diagnosis,
        syndrome_diagnosis_date=None,
        syndrome_name=None,
    )

    context = {
        'syndrome': syndrome,
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context
    )

    return response


"""
Syndromes
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def edit_syndrome(request, syndrome_id):
    """
    HTMX post request from episodes.html partial on button click to add new episode
    """
    syndrome = Syndrome.objects.get(pk=syndrome_id)

    keywords = Keyword.objects.all()

    context = {
        'syndrome': syndrome,
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
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
        'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
        'nonepilepsy_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'syncopes': sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        'behavioural': sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)),
        'sleep': sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        'paroxysms': sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        'migraines': sorted(MIGRAINES, key=itemgetter(1)),
        'nonepilepsy_miscellaneous': sorted(EPIS_MISC, key=itemgetter(1)),
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_full_access', 'trust_audit_team_full_access')
def remove_syndrome(request, syndrome_id):
    """
    POST request on button click from episodes partial in multiaxial_diagnosis form
    Deletes syndrome from table
    """
    syndrome = Syndrome.objects.get(pk=syndrome_id)
    multiaxial_diagnosis = syndrome.multiaxial_diagnosis
    Syndrome.objects.get(pk=syndrome_id).delete()
    syndromes = Syndrome.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('syndrome_diagnosis_date')

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'syndromes': syndromes
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndromes.html',
        context=context
    )

    return response


@login_required
def close_syndrome(request, syndrome_id):
    """
    Call back from onclick of close episode in episode.html
    returns the episodes list partial
    """
    syndrome = Syndrome.objects.get(
        pk=syndrome_id)
    multiaxial_diagnosis = syndrome.multiaxial_diagnosis

    # if all the fields are none this was not completed - delete the record
    if completed_fields(syndrome) == 0:
        syndrome.delete()

    syndromes = Syndrome.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('syndrome_diagnosis_date')

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'syndromes': syndromes
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndromes.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_present(request, multiaxial_diagnosis_id):
    """
# POST request from the syndrome partial in the multiaxial_description_form
# Updates model and returns the syndrome partial
"""
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)
    if request.htmx.trigger_name == 'button-true':
        multiaxial_diagnosis.syndrome_present = True
        multiaxial_diagnosis.updated_at = timezone.now()
        multiaxial_diagnosis.updated_by = request.user
        multiaxial_diagnosis.save()
    elif request.htmx.trigger_name == 'button-false':

        multiaxial_diagnosis.syndrome_present = False
        multiaxial_diagnosis.updated_at = timezone.now()
        multiaxial_diagnosis.updated_by = request.user
        multiaxial_diagnosis.save()
        # delete any associated syndromes
        if Syndrome.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis).exists():
            Syndrome.objects.filter(
                multiaxial_diagnosis=multiaxial_diagnosis).delete()
    else:
        print("Some mistake happened")
        # TODO need to handle this

    syndromes = Syndrome.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).all()

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "syndromes": syndromes
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome_section.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def epilepsy_cause_known(request, multiaxial_diagnosis_id):
    """
# POST request from the syndrome partial in the multiaxial_description_form
# Updates model and returns the syndrome partial
"""
    if request.htmx.trigger_name == 'button-true':
        MultiaxialDiagnosis.objects.filter(pk=multiaxial_diagnosis_id).update(
            epilepsy_cause_known=True,
            updated_at=timezone.now(),
            updated_by=request.user
        )
    elif request.htmx.trigger_name == 'button-false':
        MultiaxialDiagnosis.objects.filter(pk=multiaxial_diagnosis_id).update(
            epilepsy_cause_known=False,
            epilepsy_cause=None,
            epilepsy_cause_categories=[],
            updated_at=timezone.now(),
            updated_by=request.user
        )
    else:
        print("Some mistake happened")
        # TODO need to handle this

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    ecl = '<< 363235000'
    epilepsy_causes = fetch_ecl(ecl)

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
        "epilepsy_causes": epilepsy_causes
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/epilepsy_causes/epilepsy_cause_section.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def epilepsy_cause(request, multiaxial_diagnosis_id):
    """
    POST request on change select from epilepsy_causes partial
    Choices for causes fed from SNOMED server
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=MultiaxialDiagnosis,
            model_id=multiaxial_diagnosis_id,
            field_name='epilepsy_cause',
            page_element='select'
        )
    except ValueError as error:
        error_message = error

    # SNOMED term populating epilepsy cause dropdown
    ecl = '<< 363235000'
    epilepsy_causes = fetch_ecl(ecl)

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    context = {
        'epilepsy_causes': sorted(epilepsy_causes, key=itemgetter('preferredTerm')),
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/epilepsy_causes/epilepsy_causes.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def epilepsy_cause_categories(request, multiaxial_diagnosis_id):
    """
    POST from multiple select in epilepsy_causes partial
    """

    epilepsy_cause_category = request.htmx.trigger_name

    if epilepsy_cause_category:

        multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
            pk=multiaxial_diagnosis_id)
        if epilepsy_cause_category in multiaxial_diagnosis.epilepsy_cause_categories:
            multiaxial_diagnosis.epilepsy_cause_categories.remove(
                epilepsy_cause_category)
        else:
            multiaxial_diagnosis.epilepsy_cause_categories.append(
                epilepsy_cause_category)

        multiaxial_diagnosis.save()

    else:
        print(
            f"category is {epilepsy_cause_category}. This is an error that needs handling")
        # TODO handle this error

    context = {
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
        "multiaxial_diagnosis": multiaxial_diagnosis,
        # 'epilepsy_causes': sorted(epilepsy_causes, key=itemgetter('preferredTerm')),
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/epilepsy_causes/epilepsy_cause_categories.html',
        context=context
    )

    return response


"""
Comorbidities
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def relevant_impairments_behavioural_educational(request, multiaxial_diagnosis_id):
    """
    POST request from
    """

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)
    if request.htmx.trigger_name == 'button-true':
        multiaxial_diagnosis.relevant_impairments_behavioural_educational = True
        multiaxial_diagnosis.save()
    elif request.htmx.trigger_name == 'button-false':
        # save and delete any associated comorbidities
        multiaxial_diagnosis.relevant_impairments_behavioural_educational = False
        multiaxial_diagnosis.updated_at = timezone.now()
        multiaxial_diagnosis.updated_by = request.user
        if Comorbidity.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis).exists():
            Comorbidity.objects.filter(
                multiaxial_diagnosis=multiaxial_diagnosis).delete()
        multiaxial_diagnosis.save()
    else:
        print(
            "Some kind of error - this will need to be raised and returned to template")
        return HttpResponse("Error")

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'comorbidities': Comorbidity.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis).all(),
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidity_section.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def add_comorbidity(request, multiaxial_diagnosis_id):
    """
    POST request from comorbidities_section partial
    """
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    comorbidity = Comorbidity.objects.create(
        multiaxial_diagnosis=multiaxial_diagnosis,
        comorbidity_diagnosis_date=None,
        comorbidity_diagnosis=None
    )

    comorbidity = Comorbidity.objects.get(pk=comorbidity.pk)
    ecl = '<< 35919005'
    comorbidity_choices = fetch_ecl(ecl)

    context = {
        'comorbidity': comorbidity,
        'comorbidity_choices': sorted(comorbidity_choices, key=itemgetter('preferredTerm')),
    }

    response = recalculate_form_generate_response(
        model_instance=comorbidity.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidity.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def edit_comorbidity(request, comorbidity_id):
    """
    POST request from comorbidities.html partial on button click to edit episode
    """
    comorbidity = Comorbidity.objects.get(pk=comorbidity_id)
    ecl = '<< 35919005'
    comorbidity_choices = fetch_ecl(ecl)

    context = {
        'comorbidity': comorbidity,
        'comorbidity_choices': sorted(comorbidity_choices, key=itemgetter('preferredTerm')),
    }

    response = recalculate_form_generate_response(
        model_instance=comorbidity.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidity.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_full_access', 'trust_audit_team_full_access')
def remove_comorbidity(request, comorbidity_id):
    """
    POST request from comorbidities.html partial on button click to edit episode
    """
    comorbidity = Comorbidity.objects.get(pk=comorbidity_id)
    multiaxial_diagnosis = comorbidity.multiaxial_diagnosis
    Comorbidity.objects.filter(pk=comorbidity_id).delete()

    comorbidities = Comorbidity.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).all()

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'comorbidities': comorbidities,
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidities.html',
        context=context
    )

    return response


@login_required
def close_comorbidity(request, comorbidity_id):
    """
    Call back from onclick of close comorbidity in comorbidity.html
    returns the episodes list partial
    """
    comorbidity = Comorbidity.objects.get(
        pk=comorbidity_id)
    multiaxial_diagnosis = comorbidity.multiaxial_diagnosis

    # if all the fields are none this was not completed - delete the record
    if completed_fields(comorbidity) == 0:
        comorbidity.delete()

    comorbidities = Comorbidity.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).order_by('comorbidity_diagnosis_date')

    context = {
        'multiaxial_diagnosis': multiaxial_diagnosis,
        'comorbidities': comorbidities
    }

    response = recalculate_form_generate_response(
        model_instance=comorbidity.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidities.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def comorbidity_diagnosis_date(request, comorbidity_id):
    """
    POST request from comorbidity partial with comorbidity_diagnosis_date
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Comorbidity,
            model_id=comorbidity_id,
            field_name='comorbidity_diagnosis_date',
            page_element='date_field'
        )
    except ValueError as error:
        error_message = error

    comorbidity = Comorbidity.objects.get(pk=comorbidity_id)

    ecl = '<< 35919005'
    comorbidity_choices = fetch_ecl(ecl)

    context = {
        'comorbidity': comorbidity,
        'comorbidity_choices': sorted(comorbidity_choices, key=itemgetter('preferredTerm')),
    }

    response = recalculate_form_generate_response(
        model_instance=comorbidity.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidity.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def comorbidity_diagnosis(request, comorbidity_id):
    """
    POST request on change select from comorbidity partial
    Choices for causes fed from SNOMED server
    """

    # 35919005 |Pervasive developmental disorder (disorder)|

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Comorbidity,
            model_id=comorbidity_id,
            field_name='comorbidity_diagnosis',
            page_element='snomed_select'
        )
    except ValueError as error:
        error_message = error

    ecl = '<< 35919005'
    comorbidity_choices = fetch_ecl(ecl)

    comorbidity = Comorbidity.objects.get(
        pk=comorbidity_id)

    context = {
        'comorbidity_choices': sorted(comorbidity_choices, key=itemgetter('preferredTerm')),
        "comorbidity": comorbidity,
    }

    response = recalculate_form_generate_response(
        model_instance=comorbidity.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidity.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def comorbidities(request, multiaxial_diagnosis_id):
    """
    POST request from comorbidity partial to replace it with table
    """
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)
    comorbidities = Comorbidity.objects.filter(
        multiaxial_diagnosis=multiaxial_diagnosis).all()

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "comorbidities": comorbidities,
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/comorbidities/comorbidities.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mental_health_screen(request, multiaxial_diagnosis_id):
    """
    POST request callback for mental_health_screen toggle
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=MultiaxialDiagnosis,
            model_id=multiaxial_diagnosis_id,
            field_name='mental_health_screen',
            page_element='toggle_button'
        )
    except ValueError as error:
        error_message = error

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "mental_health_issues_choices": NEUROPSYCHIATRIC
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/mental_health_section.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mental_health_issue_identified(request, multiaxial_diagnosis_id):
    """
    POST request callback for mental_health_issue_identified toggle
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=MultiaxialDiagnosis,
            model_id=multiaxial_diagnosis_id,
            field_name='mental_health_issue_identified',
            page_element='toggle_button'
        )
    except ValueError as error:
        error_message = error

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    # tidy up
    if not multiaxial_diagnosis.mental_health_issue_identified:
        # if no issue identified, remove any previously stored mental health issues
        multiaxial_diagnosis.mental_health_issue = None
        multiaxial_diagnosis.updated_at = timezone.now(),
        multiaxial_diagnosis.updated_by = request.user
        multiaxial_diagnosis.save()

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "mental_health_issues_choices": NEUROPSYCHIATRIC
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/mental_health_section.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mental_health_issue(request, multiaxial_diagnosis_id):
    """
    POST callback from mental_health_issue multiple toggle
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=MultiaxialDiagnosis,
            model_id=multiaxial_diagnosis_id,
            field_name='mental_health_issue',
            page_element='single_choice_multiple_toggle_button'
        )
    except ValueError as error:
        error_message = error

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        pk=multiaxial_diagnosis_id)

    context = {
        "multiaxial_diagnosis": multiaxial_diagnosis,
        "mental_health_issues_choices": NEUROPSYCHIATRIC,
    }

    response = recalculate_form_generate_response(
        model_instance=multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/mental_health_section.html',
        context=context,
        error_message=error_message
    )

    return response
