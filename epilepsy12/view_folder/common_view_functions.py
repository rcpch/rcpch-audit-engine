from datetime import datetime, date
from django.utils import timezone
from django_htmx.http import trigger_client_event
from django.shortcuts import render
from psycopg2 import DatabaseError
from epilepsy12.models.antiepilepsy_medicine import AntiEpilepsyMedicine
from epilepsy12.models.registration import Registration

from epilepsy12.models.site import Site

from ..models import AuditProgress, Episode, Syndrome, Comorbidity, Management


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

    if verbose_name_underscored == 'registration':
        registration = model_instance
    else:
        registration = model_instance.registration

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
            if getattr(model_instance, field.name) is not None:
                if field.name == 'epilepsy_cause_categories' or field.name == 'description':
                    if len(getattr(model_instance, field.name)) > 0:
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

                    if medicine.medicine_name:
                        cumulative_score += 1
                    if medicine.antiepilepsy_medicine_start_date:
                        cumulative_score += 1
                    if medicine.antiepilepsy_medicine_risk_discussed:
                        cumulative_score += 1

                    if medicine.medicine_id == 21 and model_instance.registration.case.sex == 2:
                        # essential fields are:
                        # 'is_a_pregnancy_prevention_programme_needed'
                        cumulative_score += 1
                        if medicine.is_a_pregnancy_prevention_programme_needed:
                            # essential fields are:
                            # 'is_a_pregnancy_prevention_programme_in_place
                            cumulative_score += 1
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
                    # 'antiepilepsy_medicine_stop_date', 'antiepilepsy_medicine_risk_discussed'
                    cumulative_score += 4
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
        return ['id', 'management', 'assessment', 'investigations', 'multiaxial_diagnosis', 'registration', 'epilepsycontext', 'firstpaediatricassessment', 'registration_close_date', 'registration_date_one_year_on', 'cohort', 'case', 'audit_progress', 'created_by', 'created_at', 'updated_by', 'updated_at']
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
        return len(['medicine_name', 'antiepilepsy_medicine_start_date', 'antiepilepsy_medicine_stop_date', 'antiepilepsy_medicine_risk_discussed', 'is_a_pregnancy_prevention_programme_needed', 'is_a_pregnancy_prevention_programme_in_place'])
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
                elif site.site_is_general_paediatric_centre:
                    cumulative_score += 1
                elif site.site_is_paediatric_neurology_centre:
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
                    # 'antiepilepsy_medicine_stop_date', 'antiepilepsy_medicine_risk_discussed'
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
        is_earliest_date=None):
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
