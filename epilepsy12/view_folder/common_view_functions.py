from django_htmx.http import trigger_client_event
from django.shortcuts import render
from django.db import IntegrityError

from ..models import AuditProgress, Episode, Syndrome, Comorbidity


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

    if model_instance.__class__.__name__ == 'MultiaxialDiagnosis':
        # also need to count associated records in Episode, Syndrome and Comorbidity
        episodes = Episode.objects.filter(
            multiaxial_diagnosis=model_instance).all()
        syndromes = Syndrome.objects.filter(
            multiaxial_diagnosis=model_instance).all()
        comorbidities = Comorbidity.objects.filter(
            multiaxial_diagnosis=model_instance).all()
        if episodes.count() > 0:
            for episode in episodes:
                all_completed_fields += completed_fields(episode)
        if syndromes.count() > 0:
            for syndrome in syndromes:
                all_completed_fields += completed_fields(syndrome)
        if comorbidities.count() > 0:
            for comorbidity in comorbidities:
                all_completed_fields += completed_fields(comorbidity)

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
        if field.name not in avoid_fields(model_instance):
            if getattr(model_instance, field.name) is not None:
                if field.name == 'epilepsy_cause_categories' or field.name == 'description':
                    if len(getattr(model_instance, field.name)) > 0:
                        counter += 1
                else:
                    counter += 1

    return counter


def total_fields_expected(model_instance):
    """
    a minimum total fields would be:
    """

    model_class_name = model_instance.__class__.__name__
    # get the minimum number of fields for this model
    cumulative_score = scoreable_fields_for_model_class_name(
        model_class_name=model_class_name)

    if model_instance.__class__.__name__ == "MultiaxialDiagnosis":
        # count episodes - note
        # at least one episode must be epileptic

        episodes = Episode.objects.filter(
            multiaxial_diagnosis=model_instance
        ).all()

        # loop through all episodes and count the fields
        # if there are none, return the minimum score for an epileptic seizure
        cumulative_score += count_episode_fields(episodes)

        # syndromes are optional but if present add essential fields
        if model_instance.syndrome_present:
            if Syndrome.objects.filter(
                multiaxial_diagnosis=model_instance
            ).exists():
                # there are syndromes - increase total to include essential fields per syndrome
                number_of_syndromes = Syndrome.objects.filter(
                    multiaxial_diagnosis=model_instance
                ).count()
                cumulative_score += (scoreable_fields_for_model_class_name(
                    'Syndrome') * number_of_syndromes)
            else:
                # no syndromes yet but user indicated present - add essential fields for syndromes
                cumulative_score += scoreable_fields_for_model_class_name(
                    'Syndrome')

        # if a cause for the epilepsy is know other essential fields must be included
        if model_instance.epilepsy_cause_known:
            # essential fields include
            # epilepsy_cause
            # epilepsy_cause_categories - this is an array, length must be greater than one
            cumulative_score += 2

        if model_instance.relevant_impairments_behavioural_educational:
            # there are comorbidities - add essential comorbidities
            number_of_comorbidities = Comorbidity.objects.filter(
                multiaxial_diagnosis=model_instance).count()
            essential_fields_per_comorbidity = scoreable_fields_for_model_class_name(
                'Comorbidity')
            if number_of_comorbidities < 1:
                # comorbidities not yet scored but user has indicated there are some present
                # increase the total by minimum number required
                cumulative_score += essential_fields_per_comorbidity
            else:
                cumulative_score += (essential_fields_per_comorbidity *
                                     number_of_comorbidities)

        if model_instance.mental_health_issue_identified:
            # essential fields increase to include
            # mental_health_issue
            cumulative_score += 1

    return cumulative_score


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
    elif verbose_name_underscored == 'management':
        return ['id', 'registration', 'antiepilepsymedicine', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif verbose_name_underscored in ['syndrome', 'comorbidity']:
        return ['id', 'multiaxial_diagnosis', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif verbose_name_underscored == 'episode':
        return ['id', 'multiaxial_diagnosis', 'description_keywords', 'created_by', 'created_at', 'updated_by', 'updated_at']
    else:
        raise ValueError(
            f'{verbose_name_underscored} not found to return fields to avoid in form calculation.')


def scoreable_fields_for_model_class_name(model_class_name):
    """
    Returns the minimum number of scoreable fields best on the model instance at the time
    """

    if model_class_name == 'EpilepsyContext':
        # Essential fields
        return len(['previous_febrile_seizure', 'previous_acute_symptomatic_seizure', 'is_there_a_family_history_of_epilepsy', 'previous_neonatal_seizures', 'diagnosis_of_epilepsy_withdrawn', 'were_any_of_the_epileptic_seizures_convulsive', 'experienced_prolonged_generalized_convulsive_seizures', 'experienced_prolonged_focal_seizures'])
    elif model_class_name == 'FirstPaediatricAssessment':
        return len(['first_paediatric_assessment_in_acute_or_nonacute_setting', 'has_number_of_episodes_since_the_first_been_documented', 'general_examination_performed', 'neurological_examination_performed', 'developmental_learning_or_schooling_problems', 'behavioural_or_emotional_problems'])
    elif model_class_name == 'MultiaxialDiagnosis':
        # minimum fields in multiaxial_diagnosis include:
        # at least one episode that is epileptic fully completed
        return len(['syndrome_present', 'epilepsy_cause_known', 'relevant_impairments_behavioural_educational', 'mental_health_screen', 'mental_health_issue_identified'])
    elif model_class_name == 'Episode':
        # returns minimum number of fields that could be scored for an epileptic episode
        return len(['seizure_onset_date', 'seizure_onset_date_confidence', 'episode_definition', 'has_description_of_the_episode_or_episodes_been_gathered', 'epilepsy_or_nonepilepsy_status'])
    elif model_class_name == 'Syndrome':
        return len(['syndrome_diagnosis_date', 'syndrome_name'])
    elif model_class_name == 'Comorbidity':
        return len(['comorbidity_diagnosis_date', 'comorbidity_diagnosis'])
    else:
        raise ValueError(
            f'{model_class_name} does not exist to calculate minimum number of scoreable fields.')


def count_episode_fields(all_episodes):
    """
    loops through each episode associated with a multiaxial diagnosis and add up expected number of fields
    based selections so far
    """
    cumulative_score = 0
    is_epilepsy = False
    epilepsy_status_known = 0

    if all_episodes.count() == 0:
        # no episodes so far
        return scoreable_fields_for_model_class_name('Episode')

    for episode in all_episodes:
        # essential fields already accounted for are:
        # seizure_onset_date
        # seizure_onset_date_confidence
        # episode_definition
        # has_description_of_the_episode_or_episodes_been_gathered
        # epilepsy_or_nonepilepsy_status
        cumulative_score += 5

        if episode.has_description_of_the_episode_or_episodes_been_gathered:
            # essential fields are:
            # description
            cumulative_score += 1
        if episode.epilepsy_or_nonepilepsy_status == "E":
            # epileptic seizure: essential fields:
            # epileptic_seizure_onset_type

            is_epilepsy = True
            epilepsy_status_known += 1

            cumulative_score += 1
            if episode.epileptic_seizure_onset_type == 'GO':
                # generalised onset: essential fields
                # epileptic_generalised_onset
                cumulative_score += 1
            elif episode.epileptic_seizure_onset_type == 'FO':
                # focal onset
                # minimum score is laterality
                cumulative_score + 1
            else:
                # either unclassified or unknown onset
                # no further score
                cumulative_score += 0
        elif episode.epilepsy_or_nonepilepsy_status == "NE":
            # nonepileptic seizure - essential fields:
            # nonepileptic_seizure_unknown_onset
            # nonepileptic_seizure_type
            # AND ONE of behavioural/migraine/misc/paroxysmal/sleep related/syncope - essential fields:
            # nonepileptic_seizure_behavioural or
            # nonepileptic_seizure_migraine or
            # nonepileptic_seizure_miscellaneous or
            # nonepileptic_seizure_paroxysmal or
            # nonepileptic_seizure_sleep
            # nonepileptic_seizure_syncope
            epilepsy_status_known += 1

            cumulative_score += 3
        elif episode.epilepsy_or_nonepilepsy_status == "U":
            # uncertain status
            cumulative_score += 0
            epilepsy_status_known += 1

    if is_epilepsy or not epilepsy_status_known == all_episodes.count():
        # at least one episode is epileptic or no episodes are as yet unscored
        return cumulative_score
    else:
        # none of the episodes are epileptic
        # increase the total by the minimum number of fields for an epileptic episode
        cumulative_score += scoreable_fields_for_model_class_name('Episode')
        return cumulative_score
