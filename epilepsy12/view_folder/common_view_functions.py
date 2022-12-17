from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django_htmx.http import trigger_client_event
from django.shortcuts import render
from django.db.models import Q
from psycopg2 import DatabaseError
from epilepsy12.models.antiepilepsy_medicine import AntiEpilepsyMedicine
from epilepsy12.models.registration import Registration

from epilepsy12.models.site import Site

from ..models import AuditProgress, Episode, Syndrome, Comorbidity, Management
from ..general_functions import current_cohort_start_date, first_tuesday_in_january


def recalculate_form_generate_response(model_instance, request, context, template, error_message=None):
    """
    calculates form scores, creates response object and attaches htmx trigger to refresh steps widget
    Params:
    request
    model instance
    context
    template name
    error message - if not supplied an empty string is attached
    """

    # add errors to context
    context.update({
        'error_message': error_message
    })

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

    # use the model instance to identify its verbose name to match the relevant field in the AuditProgress model
    verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')

    all_completed_fields = completed_fields(model_instance)
    all_expected_fields = total_fields_expected(model_instance)

    all_completed_fields += number_of_completed_fields_in_related_models(
        model_instance)

    update_fields = {
        f'{verbose_name_underscored}_total_expected_fields': all_expected_fields,
        f'{verbose_name_underscored}_total_completed_fields': all_completed_fields,
        f'{verbose_name_underscored}_complete': all_completed_fields == all_expected_fields,
    }

    # all models are related to registration, except registration itself
    if verbose_name_underscored == 'registration':
        registration = model_instance
    else:
        registration = model_instance.registration

    calculate_kpis(registration_instance=registration)

    try:
        AuditProgress.objects.filter(
            registration=registration).update(**update_fields)
    except DatabaseError as error:
        raise Exception(error)


def completed_fields(model_instance):
    """
    Test for all completed fields
    Returns an integer number of completed fields for a given model instance.
    """
    fields = model_instance._meta.get_fields()
    counter = 0
    fields_to_avoid = avoid_fields(model_instance)

    for field in fields:
        if field.name not in fields_to_avoid:
            if getattr(model_instance, field.name, ()) is not None:
                if field.name == 'epilepsy_cause_categories' or field.name == 'description':
                    if len(getattr(model_instance, field.name)) > 0:
                        counter += 1
                else:
                    if field.name in ['focal_onset_atonic', 'focal_onset_clonic', 'focal_onset_epileptic_spasms', 'focal_onset_hyperkinetic', 'focal_onset_myoclonic', 'focal_onset_tonic', 'focal_onset_focal_to_bilateral_tonic_clonic', 'focal_onset_automatisms', 'focal_onset_impaired_awareness', 'focal_onset_gelastic', 'focal_onset_autonomic', 'focal_onset_behavioural_arrest', 'focal_onset_cognitive', 'focal_onset_emotional', 'focal_onset_sensory', 'focal_onset_centrotemporal', 'focal_onset_temporal', 'focal_onset_frontal', 'focal_onset_parietal', 'focal_onset_occipital', 'focal_onset_right', 'focal_onset_left']:
                        if getattr(model_instance, field.name, ()) == True:
                            # only count the true values in the radio buttons in focal epilepsy to do with focality
                            if field.name in ['focal_onset_right', 'focal_onset_left']:
                                counter += 1
                    else:
                        counter += 1

    return counter


def total_fields_expected(model_instance):
    """
    returns as expected fields for a given model instance, based on user selections
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

    elif model_class_name == 'Assessment':
        if model_instance.consultant_paediatrician_referral_made:
            # add essential fields: date referred, date seen, centre
            cumulative_score += 3
        if model_instance.paediatric_neurologist_referral_made:
            # add essential fields: date referred, date seen, centre
            cumulative_score += 3
        if model_instance.childrens_epilepsy_surgical_service_referral_made:
            # add essential fields: date referred, date seen, centre
            cumulative_score += 3
        if model_instance.epilepsy_specialist_nurse_referral_made:
            # add essential fields: date referred, date seen
            cumulative_score += 2

    elif model_class_name == 'Investigations':
        if model_instance.eeg_indicated:
            # add essential fields: request date, performed_date
            cumulative_score += 2
        if model_instance.mri_indicated:
            # add essential fields: request date, performed_date
            cumulative_score += 2

    elif model_class_name == 'Management':
        # also need to count associated records in AntiepilepsyMedicines
        if model_instance.has_an_aed_been_given:
            # antiepilepsy drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance,
                is_rescue_medicine=False
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed'
                    # NOTE 'antiepilepsy_medicine_stop_date' is not an essential field

                    cumulative_score += 3

                    if medicine.medicine_id == 21 and model_instance.registration.case.sex == 2:
                        # essential fields are:
                        # 'is_a_pregnancy_prevention_programme_needed'
                        cumulative_score += 1
                        if medicine.is_a_pregnancy_prevention_programme_needed:
                            # essential fields are:
                            # 'is_a_pregnancy_prevention_programme_in_place, 'has_a_valproate_annual_risk_acknowledgement_form_been_completed'
                            cumulative_score += 2
            else:
                # user has said AED given but not scored yet
                cumulative_score += scoreable_fields_for_model_class_name(
                    'AntiEpilepsyMedicine')

        if model_instance.has_rescue_medication_been_prescribed:
            # rescue drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance,
                is_rescue_medicine=True
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed'
                    cumulative_score += 3
            else:
                # user has said AED given but not scored yet
                cumulative_score += scoreable_fields_for_model_class_name(
                    'AntiEpilepsyMedicine')

        if model_instance.individualised_care_plan_in_place:
            # add essential fields:
            # individualised_care_plan_date, individualised_care_plan_has_parent_carer_child_agreement,
            # individualised_care_plan_includes_service_contact_details, individualised_care_plan_include_first_aid,
            # individualised_care_plan_parental_prolonged_seizure_care, individualised_care_plan_includes_general_participation_risk,
            # individualised_care_plan_addresses_water_safety, individualised_care_plan_addresses_sudep,
            # individualised_care_plan_includes_ehcp, has_individualised_care_plan_been_updated_in_the_last_year
            cumulative_score += 10

    elif model_class_name == 'Registration':
        # further essential field is from Site - primary site of care
        cumulative_score += 1

    return cumulative_score


def avoid_fields(model_instance):
    """
    When looping through fields and counting them as complete/incomplete, these fields depending on the model
    should be avoided
    """
    # verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')
    model_class_name = model_instance.__class__.__name__

    if model_class_name in ["FirstPaediatricAssessment",
                            "EpilepsyContext", "Assessment", "Investigations"]:
        return ['id', 'registration', 'updated_at', 'updated_by', 'created_at', 'created_by']
    elif model_class_name == 'MultiaxialDiagnosis':
        return ['id', 'registration', 'multiaxial_diagnosis', 'episode', 'syndrome', 'comorbidity', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif model_class_name == 'Management':
        return ['id', 'registration', 'antiepilepsymedicine', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif model_class_name in ['Syndrome', 'Comorbidity']:
        return ['id', 'multiaxial_diagnosis', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif model_class_name == 'Episode':
        return ['id', 'multiaxial_diagnosis', 'description_keywords', 'created_by', 'created_at', 'updated_by', 'updated_at']
    elif model_class_name == 'AntiEpilepsyMedicine':
        return ['id', 'management', 'medicine_id', 'is_rescue_medicine', 'antiepilepsy_medicine_snomed_code', 'antiepilepsy_medicine_snomed_preferred_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'antiepilepsy_medicine_stop_date']
    elif model_class_name == 'Registration':
        return ['id', 'management', 'assessment', 'investigations', 'multiaxialdiagnosis', 'registration', 'epilepsycontext', 'firstpaediatricassessment', 'registration_close_date', 'registration_date_one_year_on', 'audit_submission_date', 'cohort', 'case', 'audit_progress', 'created_by', 'created_at', 'updated_by', 'updated_at']
    else:
        raise ValueError(
            f'Form scoring error: {model_class_name} not found to return fields to avoid in form calculation.')


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
    elif model_class_name == 'Assessment':
        return len(['childrens_epilepsy_surgical_service_referral_criteria_met', 'consultant_paediatrician_referral_made', 'paediatric_neurologist_referral_made', 'childrens_epilepsy_surgical_service_referral_made', 'epilepsy_specialist_nurse_referral_made'])
    elif model_class_name == 'Investigations':
        return len(['eeg_indicated', 'twelve_lead_ecg_status', 'ct_head_scan_status', 'mri_indicated'])
    elif model_class_name == 'Management':
        return len(['has_an_aed_been_given', 'has_rescue_medication_been_prescribed', 'individualised_care_plan_in_place', 'has_been_referred_for_mental_health_support', 'has_support_for_mental_health_support'])
    elif model_class_name == 'AntiEpilepsyMedicine':
        return len(['medicine_name', 'antiepilepsy_medicine_start_date', 'antiepilepsy_medicine_risk_discussed'])
    elif model_class_name == 'Registration':
        return len(['registration_date', 'eligibility_criteria_met'])
    else:
        raise ValueError(
            f'Form scoring error: {model_class_name} does not exist to calculate minimum number of scoreable fields.')


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
                cumulative_score += 1
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


def number_of_completed_fields_in_related_models(model_instance):
    """
    Counts completed fields in models related to modelinstance passed in as parameter.
    Returns an integer number of completed fields
    If there are no related models, zero is returned.
    """
    cumulative_score = 0
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
                cumulative_score += completed_fields(episode)
        if syndromes.count() > 0:
            for syndrome in syndromes:
                cumulative_score += completed_fields(syndrome)
        if comorbidities.count() > 0:
            for comorbidity in comorbidities:
                cumulative_score += completed_fields(comorbidity)
    elif model_instance.__class__.__name__ == 'Assessment':
        # also need to count associated records in Site
        sites = Site.objects.filter(
            case=model_instance.registration.case,
            site_is_actively_involved_in_epilepsy_care=True).all()
        if sites:
            for site in sites:
                if site.site_is_childrens_epilepsy_surgery_centre:
                    cumulative_score += 1
                if site.site_is_general_paediatric_centre:
                    cumulative_score += 1
                if site.site_is_paediatric_neurology_centre:
                    cumulative_score += 1
    elif model_instance.__class__.__name__ == 'Management':
        # also need to count associated records in AntiepilepsyMedicines
        if model_instance.has_an_aed_been_given:
            # antiepilepsy drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance,
                is_rescue_medicine=False
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_stop_date', 'antiepilepsy_medicine_risk_discussed'
                    cumulative_score += completed_fields(medicine)

        if model_instance.has_rescue_medication_been_prescribed:
            # rescue drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance,
                is_rescue_medicine=True
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed'
                    cumulative_score += completed_fields(medicine)

    elif model_instance.__class__.__name__ == 'Registration':
        # also need to count associate record in Site
        if Site.objects.filter(
                case=model_instance.case,
                site_is_primary_centre_of_epilepsy_care=True,
                site_is_actively_involved_in_epilepsy_care=True).exists():
            cumulative_score += 1

    return cumulative_score


def validate_and_update_model(
        request,
        model_id,
        model,
        field_name,
        page_element,
        comparison_date_field_name=None,
        is_earliest_date=None
):
    """
    This is called from the view to update the model or return an error
    Parameters:
    request
    model_id
    model: the class, not the instance
    field_name
    page_element: string one of 'date_field', 'toggle_button', 'multiple_choice_single_toggle_button', 'multiple_choic_multiple_toggle_button', 'select', 'snomed_select', 'hospital_select'
    comparison_date_field_name: string corresponding to field name for date in model
    is_earliest_date: boolean

    It replaces the decorator @update_model as decorators can only redirect the request, 
    they cannot pass parameters to the function they wrap. This means that errors raised in updating the model
    cannot be passed back to the template so the logic has been added to this function instead.
    It is important that this function is called early on in the view function and that an updated instance of 
    the model AFTER UPDATE is put in the context that is passed back to the template.
    """
    if page_element == 'toggle_button':
        # toggle button
        # the trigger_name of the element here corresponds to whether true or false has been selected

        if request.htmx.trigger_name == 'button-true':
            field_value = True
        elif request.htmx.trigger_name == 'button-false':
            field_value = False
        else:
            # an error has occurred
            print('Error has occurred')

    elif page_element == 'multiple_choice_multiple_toggle_button' or page_element == 'single_choice_multiple_toggle_button':
        # multiple_choice_multiple_toggle_button
        field_value = request.htmx.trigger_name

    elif page_element == 'date_field':
        field_value = datetime.strptime(request.POST.get(
            request.htmx.trigger_name), "%Y-%m-%d").date()

    elif page_element == 'select' or page_element == 'snomed_select':
        field_value = request.POST.get(request.htmx.trigger_name)

    # validate

    if page_element == 'date_field':
        # date tests a bit involved
        # No date can be before the date of birth
        # If a comparison date field is supplied, the date itself might not yet have been set.
        # The earlier of the two dates cannot be in the future and cannot be later than the second if supplied.
        # The later of the two dates CAN be in the future but cannot be earlier than the first if supplied.
        # If there is no comparison date (eg registration_date) the only stipulation is that it not be in the future.
        date_valid = None

        if comparison_date_field_name:
            instance = model.objects.get(pk=model_id)
            comparison_date = getattr(
                instance, comparison_date_field_name)
            if is_earliest_date:
                if comparison_date:
                    date_valid = field_value <= comparison_date and field_value <= date.today()
                    date_error = f'The date you chose ({field_value}) cannot not be after {comparison_date} or in the future.'
                else:
                    date_valid = field_value <= date.today()
                    date_error = f'The date you chose ({field_value}) cannot not be in the future.'
                if not date_valid:
                    errors = date_error
            else:
                if comparison_date:
                    date_valid = field_value >= comparison_date
                    date_error = f'The date you chose ({field_value}) cannot not be before {comparison_date}'
                else:
                    # no other date supplied yet
                    date_valid = True
                if not date_valid:
                    errors = date_error

        elif field_value > date.today() and (is_earliest_date is None or is_earliest_date):
            # dates cannot be in the future unless they are the second of 2 dates
            date_error = f'The date you chose ({field_value}) cannot not be in the future.'
            errors = date_error
            date_valid = False
        else:
            date_valid = True

        if date_valid:
            pass
        else:
            raise ValueError(errors)

    # update the model

    # if saving a registration_date, this has to trigger the save() method to generate a cohort
    # so update() cannot be used
    # This feels like a bit of a hack so very open to suggestions on more Django way of doing this
    if field_name == 'registration_date':

        # registration_date cannot be before date of birth
        registration = Registration.objects.get(pk=model_id)
        if field_value < registration.case.date_of_birth:
            date_valid = False
            errors = f"The date you chose ({field_value.strftime('%d %B %Y')}) cannot not be before {registration.case}'s date of birth."
            raise ValueError(errors)

        # the registration date cannot be before the current cohort
        current_cohort_end_date = first_tuesday_in_january(
            current_cohort_start_date().year)+relativedelta(days=7)
        if field_value < current_cohort_start_date():
            date_valid = False
            errors = f'The date you entered cannot be before the current cohort start date ({current_cohort_start_date().strftime("%d %B %Y")})'
            raise ValueError(errors)
        elif field_value > current_cohort_end_date:
            date_valid = False
            errors = f'The date you entered cannot be after the current cohort end date ({current_cohort_end_date.strftime("%d %B %Y")})'
            raise ValueError(errors)

        else:
            registration = Registration.objects.get(pk=model_id)
            registration.registration_date = field_value
            registration.updated_at = timezone.now()
            registration.updated_by = request.user
            registration.save()
    else:
        updated_field = {
            field_name: field_value,
            'updated_at': timezone.now(),
            'updated_by': request.user
        }

        try:
            model.objects.filter(
                pk=model_id).update(**updated_field)
        except DatabaseError as error:
            raise Exception(error)


def calculate_kpis(registration_instance):
    """
    Function called on update of every field
    Identifies completed KPIs and passes these back to update AuditProgress model
    It accepts the registration instance
    """

    # child must be registered in the audit for the KPI to be counted
    is_registered = (
        registration_instance.registration_date is not None and registration_instance.eligibility_criteria_met) == True

    if not is_registered:
        # cannot proceed any further if registration incomplete.
        # In theory it should not be possible to get this far.
        return

    # 1. paediatrician_with_expertise_in_epilepsies
    # Calculation Method
    # Numerator = Number of children and young people [diagnosed with epilepsy] at first year AND (who had [input from a paediatrician with expertise in epilepsy] OR a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)
    # Denominator = Number of and young people [diagnosed with epilepsy] at first year
    paediatrician_with_expertise_in_epilepsies = 0
    if hasattr(registration_instance, 'assessment'):
        if registration_instance.assessment.consultant_paediatrician_referral_made:
            if (
                registration_instance.assessment.consultant_paediatrician_input_date <= (
                    registration_instance.registration_date + relativedelta(days=+14))
            ):
                paediatrician_with_expertise_in_epilepsies = 1
        elif registration_instance.assessment.paediatric_neurologist_referral_made:
            if (
                registration_instance.assessment.paediatric_neurologist_input_date <= (
                    registration_instance.registration_date + relativedelta(days=+14))
            ):
                paediatrician_with_expertise_in_epilepsies = 1

    # 2. epilepsy_specialist_nurse
    # Calculation Method
    # Numerator= Number of children and young people [diagnosed with epilepsy] AND who had [input from or referral to an Epilepsy Specialist Nurse] by first year
    # Denominator = Number of children and young people [diagnosed with epilepsy] at first year
    epilepsy_specialist_nurse = 0
    if hasattr(registration_instance, 'assessment'):
        if registration_instance.assessment.epilepsy_specialist_nurse_referral_made:
            if (
                registration_instance.assessment.epilepsy_specialist_nurse_input_date <= registration_instance.registration_close_date
            ) or (
                registration_instance.assessment.epilepsy_specialist_nurse_referral_date <= registration_instance.registration_close_date
            ):
                epilepsy_specialist_nurse = 1

    # 3. tertiary_input
    # Calculation Method
    # Numerator = Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]
    # Denominator = Number of children [less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year )OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] OR (Number of children less than 4 years old at first assessment with epilepsy AND  [myoclonic seizures])
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.registration_date, registration_instance.case.date_of_birth).years
    tertiary_input = 0
    if hasattr(registration_instance, 'management') and hasattr(registration_instance, 'assessment'):
        if (
            # Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy]
            age_at_first_paediatric_assessment <= 3
        ) or (
            # (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year)
            AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                is_rescue_medicine=False,
                antiepilepsy_medicine_start_date__lt=registration_instance.registration_close_date
            ).count() >= 3
        ) or (
            # (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)
            age_at_first_paediatric_assessment <= 4 and
            Episode.objects.filter(
                Q(multiaxial_diagnosis=registration_instance.multiaxial_diagnosis) &
                Q(epilepsy_or_nonepilepsy_status='E') &
                Q(epileptic_generalised_onset='MyC')
            ).exists()
        ) or (
            # (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist]
            (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met == registration_instance.assessment.paediatric_neurologist_referral_made) or
            (registration_instance.assessment.paediatric_neurologist_input_date is not None and registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met)
        ) or (
            # [evidence of referral or involvement of CESS]
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_made is not None or
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_date is not None or
            registration_instance.assessment.childrens_epilepsy_surgical_service_input_date is not None
        ):
            tertiary_input = 1

    # 4. epilepsy_surgery_referral
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy AND met [CESS criteria] at first year AND had [evidence of referral or involvement of CESS]
    # Denominator =Number of children and young people diagnosed with epilepsy AND met CESS criteria at first year
    epilepsy_surgery_referral = 0
    if hasattr(registration_instance, 'assessment'):
        if (
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met and (
                registration_instance.assessment.childrens_epilepsy_surgical_service_referral_made is not None or
                registration_instance.assessment.childrens_epilepsy_surgical_service_referral_date is not None or
                registration_instance.assessment.childrens_epilepsy_surgical_service_input_date is not None
            )
        ):
            epilepsy_surgery_referral = 1

    # 5. ECG
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year AND who have [12 lead ECG obtained]
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year
    ecg = 0
    if hasattr(registration_instance, 'epilepsy_context'):
        if (
            registration_instance.epilepsy_context.were_any_of_the_epileptic_seizures_convulsive and
            registration_instance.investigations.twelve_lead_ecg_status
        ):
            ecg = 1

    # 6. MRI
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic OR number of children aged under 2 years at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND ((who are NOT JME or JAE or CAE or BECTS) OR (number of children aged under  2 years  at first assessment with a diagnosis of epilepsy at first year))
    mri = 0
    if hasattr(registration_instance, 'multiaxial_diagnosis'):
        if (
            age_at_first_paediatric_assessment <= 2 and
            (
                registration_instance.multiaxial_diagnosis.syndrome_present and
                Syndrome.objects.filter(
                    Q(multiaxial_diagnosis=registration_instance.multiaxial_diagnosis) &
                    # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
                    ~Q(syndrome_name__in=[])
                ).exists() and (
                    registration_instance.investigations.mri_brain_reported_date <= (
                        registration_instance.investigations.mri_brain_requested_date + relativedelta(days=42))
                )
            )
        ):
            mri = 1

    # 7. assessment_of_mental_health_issues
    # Calculation Method
    # Numerator = Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health
    # Denominator = = Number of children and young people over 5 years diagnosed with epilepsy
    assessment_of_mental_health_issues = 0
    if hasattr(registration_instance, 'multiaxial_diagnosis'):
        if (
            age_at_first_paediatric_assessment >= 5
        ) and (
            registration_instance.multiaxial_diagnosis.mental_health_screen
        ):
            assessment_of_mental_health_issues = 1

    # 8. mental_health_support
    # Calculation Method
    # Numerator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate AND annual risk acknowledgement forms completed AND pregnancy prevention programme in place
    # Denominator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate
    mental_health_support = 0
    if hasattr(registration_instance, 'management'):
        if(
            age_at_first_paediatric_assessment >= 12 and
            registration_instance.case.sex == 2
        ) and (
            registration_instance.management.has_an_aed_been_given and
            AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                medicine_id=21,
                is_a_pregnancy_prevention_programme_needed=True,
                has_a_valproate_annual_risk_acknowledgement_form_been_completed=True
            ).exists()
        ):
            mental_health_support = 1

    # 9. comprehensive_care_planning_agreement
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with an individualised epilepsy document or copy clinic letter that includes care planning information )AND evidence of agreement AND care plan is up to date including elements where appropriate as below
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    comprehensive_care_planning_agreement = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_in_place
        ):
            comprehensive_care_planning_agreement = 1

    # 10. patient_held_individualised_epilepsy_document
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with individualised epilepsy document or copy clinic letter that includes care planning information )
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    patient_held_individualised_epilepsy_document = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
        ):
            patient_held_individualised_epilepsy_document = 1

    # 11. care_planning_has_been_updated_when_necessary

    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    care_planning_has_been_updated_when_necessary = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
        ):
            care_planning_has_been_updated_when_necessary = 1

    # 12. comprehensive_care_planning_content
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND evidence of written prolonged seizures plan if prescribed rescue medication AND evidence of discussion regarding water safety AND first aid AND participation and risk AND service contact details AND SUDEP
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    comprehensive_care_planning_content = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.has_rescue_medication_been_prescribed and
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care and
            registration_instance.management.individualised_care_plan_include_first_aid and
            registration_instance.management.individualised_care_plan_addresses_water_safety and
            registration_instance.management.individualised_care_plan_includes_service_contact_details and
            registration_instance.management.individualised_care_plan_includes_general_participation_risk and
            registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            comprehensive_care_planning_content = 1

    # 13. parental_prolonged_seizures_care_plan
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication
    parental_prolonged_seizures_care_plan = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.has_rescue_medication_been_prescribed and
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
        ):
            parental_prolonged_seizures_care_plan = 1

    # 14. water_safety
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    water_safety = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_addresses_water_safety
        ):
            water_safety = 1

    # 15. first_aid
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    first_aid = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_include_first_aid
        ):
            first_aid = 1

    # 16. general_participation_and_risk
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    general_participation_and_risk = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_includes_general_participation_risk
        ):
            general_participation_and_risk = 1

    # 17. service_contact_details
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    service_contact_details = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_includes_service_contact_details
        ):
            service_contact_details = 1

    # 18. sudep
    # Calculation Method
    # Numerator = Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP AND evidence of a written prolonged seizures plan at first year
    # Denominator = Number of children diagnosed with epilepsy at first year
    sudep = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care and
            registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            sudep = 1

    # 19. school_individual_healthcare_plan
    # Calculation Method
    # Numerator = Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP
    # Denominator =Number of children and young people aged 5 years and above diagnosed with epilepsy at first year
    school_individual_healthcare_plan = 0
    if hasattr(registration_instance, 'management'):
        if (
            age_at_first_paediatric_assessment >= 5
        ) and (
            registration_instance.management.individualised_care_plan_includes_ehcp
        ):
            school_individual_healthcare_plan = 1

    """
    Store the KPIs in AuditProgress
    """

    kpis = {
        'paediatrician_with_expertise_in_epilepsies': paediatrician_with_expertise_in_epilepsies,
        'epilepsy_specialist_nurse': epilepsy_specialist_nurse,
        'tertiary_input': tertiary_input,
        'epilepsy_surgery_referral': epilepsy_surgery_referral,
        'ecg': ecg,
        'mri': mri,
        'assessment_of_mental_health_issues': assessment_of_mental_health_issues,
        'mental_health_support': mental_health_support,
        'comprehensive_care_planning_agreement': comprehensive_care_planning_agreement,
        'patient_held_individualised_epilepsy_document': patient_held_individualised_epilepsy_document,
        'care_planning_has_been_updated_when_necessary': care_planning_has_been_updated_when_necessary,
        'comprehensive_care_planning_content': comprehensive_care_planning_content,
        'parental_prolonged_seizures_care_plan': parental_prolonged_seizures_care_plan,
        'water_safety': water_safety,
        'first_aid': first_aid,
        'general_participation_and_risk': general_participation_and_risk,
        'service_contact_details': service_contact_details,
        'sudep': sudep,
        'school_individual_healthcare_plan': school_individual_healthcare_plan,
    }

    AuditProgress.objects.filter(
        pk=registration_instance.audit_progress.pk).update(**kpis)
