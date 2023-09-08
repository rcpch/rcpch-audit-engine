from dateutil import relativedelta
from datetime import date

# 3rd Party Imports
from django_htmx.http import trigger_client_event
from django.shortcuts import render
from psycopg2 import DatabaseError
from epilepsy12.models_folder.audit_progress import AuditProgress
from epilepsy12.models_folder.episode import Episode
from epilepsy12.models_folder.syndrome import Syndrome
from epilepsy12.models_folder.comorbidity import Comorbidity
from epilepsy12.models_folder.antiepilepsy_medicine import AntiEpilepsyMedicine
from epilepsy12.models_folder.epilepsy12_site import Site

# E12 imports
from .calculate_kpis import calculate_kpis
from epilepsy12.constants import (
    Registration_minimum_scorable_fields,
    EpilepsyContext_minimum_scorable_fields,
    FirstPaediatricAssessment_minimum_scorable_fields,
    MultiaxialDiagnosis_minimum_scorable_fields,
    Episode_minimum_scorable_fields,
    Syndrome_minimum_scorable_fields,
    Comorbidity_minimum_scorable_fields,
    Assessment_minimum_scorable_fields,
    Investigations_minimum_scorable_fields,
    Management_minimum_scorable_fields,
    AntiEpilepsyMedicine_minimum_scorable_fields,
)


def recalculate_form_generate_response(
    model_instance, request, context, template, error_message=None
):
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
    context.update({"error_message": error_message})

    # calculate totals on form
    update_audit_progress(model_instance)

    response = render(request=request, template_name=template, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response, name="registration_active", params={}
    )  # reloads the form to show the active steps
    return response


def update_audit_progress(model_instance):
    """
    Calculates all completed fields and compares expected fields
    Stores these values in AuditProgress
    Accepts model instance as parameter - uses this select correct fields to update
    """

    # use the model instance to identify its verbose name to match the relevant field in the AuditProgress model
    verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(
        " ", "_"
    )

    all_completed_fields = completed_fields(model_instance)
    all_completed_fields += number_of_completed_fields_in_related_models(model_instance)

    all_expected_fields = total_fields_expected(model_instance)

    update_fields = {
        f"{verbose_name_underscored}_total_expected_fields": all_expected_fields,
        f"{verbose_name_underscored}_total_completed_fields": all_completed_fields,
        f"{verbose_name_underscored}_complete": all_completed_fields
        == all_expected_fields,
    }

    # all models are related to registration, except registration itself
    if verbose_name_underscored == "registration":
        registration = model_instance
    else:
        registration = model_instance.registration

    # update KPIs
    calculate_kpis(registration_instance=registration)

    try:
        AuditProgress.objects.filter(registration=registration).update(**update_fields)
    except DatabaseError as error:
        raise Exception(error)


# --8<-- [start:completed_fields]
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
                if (
                    field.name == "epilepsy_cause_categories"
                    or field.name == "description"
                    or field.name == "mental_health_issues"
                ):
                    if len(getattr(model_instance, field.name)) > 0:
                        counter += 1
                else:
                    if field.name in [
                        "focal_onset_atonic",
                        "focal_onset_clonic",
                        "focal_onset_epileptic_spasms",
                        "focal_onset_hyperkinetic",
                        "focal_onset_myoclonic",
                        "focal_onset_tonic",
                        "focal_onset_focal_to_bilateral_tonic_clonic",
                        "focal_onset_automatisms",
                        "focal_onset_impaired_awareness",
                        "focal_onset_gelastic",
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
                        "focal_onset_right",
                        "focal_onset_left",
                    ]:
                        if getattr(model_instance, field.name, ()) == True:
                            # only count the true values in the radio buttons in focal epilepsy to do with focality
                            if field.name in ["focal_onset_right", "focal_onset_left"]:
                                counter += 1
                    else:
                        counter += 1
    return counter


# --8<-- [end:completed_fields]


def total_fields_expected(model_instance):
    """
    Returns as expected fields for a given model instance, based on user selections.
    """

    model_class_name = model_instance.__class__.__name__
    # get the minimum number of fields for this model
    cumulative_score = scoreable_fields_for_model_class_name(
        model_class_name=model_class_name
    )

    if model_instance.__class__.__name__ == "MultiaxialDiagnosis":
        # count episodes - note
        # at least one episode must be epileptic

        episodes = Episode.objects.filter(multiaxial_diagnosis=model_instance).all()

        # loop through all episodes and count the fields
        # if there are none, return the minimum score for an epileptic seizure
        cumulative_score += count_episode_fields(episodes)

        # syndromes are optional but if present add essential fields
        if model_instance.syndrome_present:
            if Syndrome.objects.filter(multiaxial_diagnosis=model_instance).exists():
                # there are syndromes - increase total to include essential fields per syndrome
                number_of_syndromes = Syndrome.objects.filter(
                    multiaxial_diagnosis=model_instance
                ).count()
                cumulative_score += (
                    scoreable_fields_for_model_class_name("Syndrome")
                    * number_of_syndromes
                )
            else:
                # no syndromes yet but user indicated present - add essential fields for syndromes
                cumulative_score += scoreable_fields_for_model_class_name("Syndrome")

        # if a cause for the epilepsy is know other essential fields must be included
        if model_instance.epilepsy_cause_known:
            # essential fields include
            # epilepsy_cause
            # epilepsy_cause_categories - this is an array, length must be greater than one
            cumulative_score += 2

        if model_instance.relevant_impairments_behavioural_educational:
            # there are comorbidities - add essential comorbidities
            number_of_comorbidities = Comorbidity.objects.filter(
                multiaxial_diagnosis=model_instance
            ).count()
            essential_fields_per_comorbidity = scoreable_fields_for_model_class_name(
                "Comorbidity"
            )
            if number_of_comorbidities < 1:
                # comorbidities not yet scored but user has indicated there are some present
                # increase the total by minimum number required
                cumulative_score += essential_fields_per_comorbidity
            else:
                cumulative_score += (
                    essential_fields_per_comorbidity * number_of_comorbidities
                )

        if model_instance.mental_health_issue_identified:
            # essential fields increase to include
            # mental_health_issues
            cumulative_score += 1

        if model_instance.global_developmental_delay_or_learning_difficulties:
            # essential fields increase to include
            # global_developmental_delay_or_learning_difficulties_severity
            cumulative_score += 1

    elif model_class_name == "Assessment":
        if model_instance.consultant_paediatrician_referral_made:
            # add essential fields: date referred, date seen, centre
            cumulative_score += 3
        if model_instance.paediatric_neurologist_referral_made:
            # add essential fields: date referred, date seen, centre
            cumulative_score += 3
        if model_instance.childrens_epilepsy_surgical_service_referral_made:
            # add essential fields: date referred, centre
            cumulative_score += 2
        if model_instance.epilepsy_specialist_nurse_referral_made:
            # add essential fields: date referred, date seen
            cumulative_score += 2

    elif model_class_name == "Investigations":
        if model_instance.eeg_indicated:
            # add essential fields: request date, performed_date
            cumulative_score += 2
        if model_instance.mri_indicated:
            # add essential fields: request date, performed_date
            cumulative_score += 2

    elif model_class_name == "Management":
        # also need to count associated records in AntiepilepsyMedicines
        if model_instance.has_an_aed_been_given:
            # antiepilepsy drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance, is_rescue_medicine=False
            ).all()

            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed'
                    # NOTE 'antiepilepsy_medicine_stop_date' is not an essential field

                    cumulative_score += 3

                    today = date.today()
                    calculated_age = relativedelta.relativedelta(
                        today, model_instance.registration.case.date_of_birth
                    )

                    if (
                        hasattr(medicine, "medicine_entity")
                        and model_instance.registration.case.sex == 2
                        and calculated_age.years >= 12
                    ):
                        if medicine.medicine_entity is not None:
                            if (
                                medicine.medicine_entity.medicine_name
                                == "Sodium valproate"
                            ):
                                # essential fields are:
                                # 'is_a_pregnancy_prevention_programme_needed' - this is not scored
                                if medicine.is_a_pregnancy_prevention_programme_needed:
                                    # essential fields are:
                                    # 'is_a_pregnancy_prevention_programme_in_place, 'has_a_valproate_annual_risk_acknowledgement_form_been_completed'
                                    cumulative_score += 2
            else:
                # user has said AED given but not scored yet
                cumulative_score += scoreable_fields_for_model_class_name(
                    "AntiEpilepsyMedicine"
                )

        if model_instance.has_rescue_medication_been_prescribed:
            # rescue drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance, is_rescue_medicine=True
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
                    "AntiEpilepsyMedicine"
                )

        if model_instance.individualised_care_plan_in_place:
            # add essential fields:
            # individualised_care_plan_date, individualised_care_plan_has_parent_carer_child_agreement,
            # individualised_care_plan_includes_service_contact_details, individualised_care_plan_include_first_aid,
            # individualised_care_plan_parental_prolonged_seizure_care, individualised_care_plan_includes_general_participation_risk,
            # individualised_care_plan_addresses_water_safety, individualised_care_plan_addresses_sudep,
            # individualised_care_plan_includes_ehcp, has_individualised_care_plan_been_updated_in_the_last_year
            cumulative_score += 10

    elif model_class_name == "Registration":
        # further essential field is from Site - primary site of care
        cumulative_score += 1

    return cumulative_score


# TODO: should replace with dataclass constant
def avoid_fields(model_instance):
    """
    When looping through fields and counting them as complete/incomplete, these fields depending on the model
    should be avoided
    """
    # verbose_name_underscored = model_instance._meta.verbose_name.lower().replace(' ', '_')
    model_class_name = model_instance.__class__.__name__

    META_VARIABLES = [
        "id",
        "updated_at",
        "updated_by",
        "created_at",
        "created_by",
    ]

    if model_class_name in [
        "FirstPaediatricAssessment",
        "EpilepsyContext",
        "Investigations",
    ]:
        return META_VARIABLES + ["registration"]

    elif model_class_name == "Assessment":
        return META_VARIABLES + [
            "registration",
            "childrens_epilepsy_surgical_service_input_date",
        ]

    elif model_class_name == "MultiaxialDiagnosis":
        return META_VARIABLES + [
            "registration",
            "multiaxial_diagnosis",
            "episodes",
            "syndromes",
            "comorbidities",
        ]

    elif model_class_name == "Management":
        return META_VARIABLES + ["registration", "antiepilepsymedicine"]

    elif model_class_name in ["Syndrome", "Comorbidity", "Comorbidity"]:
        return META_VARIABLES + ["multiaxial_diagnosis"]

    elif model_class_name == "Episode":
        return META_VARIABLES + [
            "multiaxial_diagnosis",
            "description_keywords",
            "expected_score",
            "calculated_score",
        ]

    elif model_class_name == "AntiEpilepsyMedicine":
        return META_VARIABLES + [
            "management",
            "is_rescue_medicine",
            "antiepilepsy_medicine_stop_date",
            "is_a_pregnancy_prevention_programme_needed",
        ]

    elif model_class_name == "Registration":
        return META_VARIABLES + [
            "management",
            "assessment",
            "investigations",
            "multiaxialdiagnosis",
            "registration",
            "epilepsycontext",
            "firstpaediatricassessment",
            "registration_close_date",
            "registration_date_one_year_on",
            "audit_submission_date",
            "cohort",
            "case",
            "audit_progress",
            "kpi",
        ]

    elif model_class_name == "Medicine":
        return [
            "id",
            "conceptId",
            "term",
            "preferredTerm",
            "description",
            "snomed_ct_edition",
            "snomed_ct_version",
            "icd_code",
            "cd_version",
            "dsm_code",
            "dsm_version",
            "is_rescue",
            "history",
        ]

    else:
        raise ValueError(
            f"Form scoring error: {model_class_name} not found to return fields to avoid in form calculation."
        )


def scoreable_fields_for_model_class_name(model_class_name):
    """
    Returns the minimum number of scoreable fields based on the model instance at the time
    """

    if model_class_name == EpilepsyContext_minimum_scorable_fields.model_name:
        return len(EpilepsyContext_minimum_scorable_fields.all_fields)

    elif (
        model_class_name == FirstPaediatricAssessment_minimum_scorable_fields.model_name
    ):
        return len(FirstPaediatricAssessment_minimum_scorable_fields.all_fields)

    elif model_class_name == MultiaxialDiagnosis_minimum_scorable_fields.model_name:
        # minimum fields in multiaxial_diagnosis include:
        # at least one episode that is epileptic fully completed
        return len(MultiaxialDiagnosis_minimum_scorable_fields.all_fields)

    elif model_class_name == Episode_minimum_scorable_fields.model_name:
        # returns minimum number of fields that could be scored for an epileptic episode
        return len(Episode_minimum_scorable_fields.all_fields)

    elif model_class_name == Syndrome_minimum_scorable_fields.model_name:
        return len(Syndrome_minimum_scorable_fields.all_fields)

    elif model_class_name == Comorbidity_minimum_scorable_fields.model_name:
        return len(Comorbidity_minimum_scorable_fields.all_fields)

    elif model_class_name == Assessment_minimum_scorable_fields.model_name:
        return len(Assessment_minimum_scorable_fields.all_fields)

    elif model_class_name == Investigations_minimum_scorable_fields.model_name:
        return len(Investigations_minimum_scorable_fields.all_fields)

    elif model_class_name == Management_minimum_scorable_fields.model_name:
        return len(Management_minimum_scorable_fields.all_fields)

    elif model_class_name == AntiEpilepsyMedicine_minimum_scorable_fields.model_name:
        return len(AntiEpilepsyMedicine_minimum_scorable_fields.all_fields)

    elif model_class_name == Registration_minimum_scorable_fields.model_name:
        return len(Registration_minimum_scorable_fields.all_fields)

    else:
        raise ValueError(
            f"Form scoring error: {model_class_name} does not exist to calculate minimum number of scoreable fields."
        )


# TODO: need to come back and write more tests with multiple cases for this as fn does multiple things. So far, have 1 test case: a fully completed Focal Onset seizure `test_count_episode_fields`
def count_episode_fields(all_episodes):
    """
    loops through each episode associated with a multiaxial diagnosis and add up expected number of fields
    based selections so far
    """
    cumulative_score = 0
    at_least_one_episode_is_epileptic = False
    epilepsy_status_known = 0

    if all_episodes.count() == 0:
        # no episodes so far
        return scoreable_fields_for_model_class_name("Episode")

    for episode in all_episodes:
        result = expected_score_for_single_episode(episode=episode)
        cumulative_score += result["cumulative_score"]
        # store the total expected in the instance
        episode.expected_score = result["cumulative_score"]
        episode.save()
        epilepsy_status_known += result["epilepsy_status_known"]
        if result["is_epilepsy"]:
            at_least_one_episode_is_epileptic = True

    # scoreable_fields_for_model_class_name('Episode')
    if at_least_one_episode_is_epileptic:
        # at least one episode is epileptic or no episodes are as yet unscored
        return cumulative_score
    else:
        # none of the episodes are epileptic
        # increase the total by the minimum number of fields for an epileptic episode
        cumulative_score += scoreable_fields_for_model_class_name("Episode")
        return cumulative_score


def expected_score_for_single_episode(episode):
    """
    returns a count of expected fields for a given episode based on what has been scored so far
    """
    # essential fields already accounted for are:
    # seizure_onset_date
    # seizure_onset_date_confidence
    # episode_definition
    # has_description_of_the_episode_or_episodes_been_gathered
    # epilepsy_or_nonepilepsy_status

    # initialize variables
    is_epilepsy = False
    cumulative_score = 0
    epilepsy_status_known = 0

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

        if episode.epileptic_seizure_onset_type == "GO":
            # generalised onset: essential fields
            # epileptic_generalised_onset
            cumulative_score += 1
        elif episode.epileptic_seizure_onset_type == "FO":
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
        if episode.nonepileptic_seizure_type == "Oth":
            cumulative_score += 2
        else:
            cumulative_score += 3
    elif episode.epilepsy_or_nonepilepsy_status == "U":
        # uncertain status
        cumulative_score += 0
        epilepsy_status_known += 1

    return {
        "cumulative_score": cumulative_score,
        "epilepsy_status_known": epilepsy_status_known,
        "is_epilepsy": is_epilepsy,
    }


def number_of_completed_fields_in_related_models(model_instance):
    """
    Counts completed fields in models related to modelinstance passed in as parameter.
    Returns an integer number of completed fields
    If there are no related models, zero is returned.
    """
    cumulative_score = 0
    if model_instance.__class__.__name__ == "MultiaxialDiagnosis":
        # also need to count associated records in Episode, Syndrome and Comorbidity
        episodes = Episode.objects.filter(multiaxial_diagnosis=model_instance).all()
        syndromes = Syndrome.objects.filter(multiaxial_diagnosis=model_instance).all()
        comorbidities = Comorbidity.objects.filter(
            multiaxial_diagnosis=model_instance
        ).all()

        if episodes.count() > 0:
            for episode in episodes:
                calculated_score = completed_fields(episode)
                # save the episode calculated score in the model instance
                episode.calculated_score = calculated_score
                episode.save()
                cumulative_score += calculated_score
        if syndromes.count() > 0:
            for syndrome in syndromes:
                cumulative_score += completed_fields(syndrome)
        if comorbidities.count() > 0:
            for comorbidity in comorbidities:
                cumulative_score += completed_fields(comorbidity)
    elif model_instance.__class__.__name__ == "Assessment":
        # also need to count associated records in Site

        sites = Site.objects.filter(
            case=model_instance.registration.case,
            site_is_actively_involved_in_epilepsy_care=True,
        ).all()

        if sites:
            for site in sites:
                if site.site_is_childrens_epilepsy_surgery_centre:
                    cumulative_score += 1
                if site.site_is_general_paediatric_centre:
                    cumulative_score += 1
                if site.site_is_paediatric_neurology_centre:
                    cumulative_score += 1
    elif model_instance.__class__.__name__ == "Management":
        # also need to count associated records in AntiepilepsyMedicines
        if model_instance.has_an_aed_been_given:
            # antiepilepsy drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance, is_rescue_medicine=False
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicineentity_medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed', and if valproate prescribed
                    # in a girl > 12y, 'is_a_pregnancy_prevention_programme_in_place'
                    # 'has_a_valproate_annual_risk_acknowledgement_form_been_completed'
                    cumulative_score += completed_fields(medicine)

        if model_instance.has_rescue_medication_been_prescribed:
            # rescue drugs
            medicines = AntiEpilepsyMedicine.objects.filter(
                management=model_instance, is_rescue_medicine=True
            ).all()
            if medicines.count() > 0:
                for medicine in medicines:
                    # essential fields are:
                    # medicine_name', 'antiepilepsy_medicine_start_date',
                    # 'antiepilepsy_medicine_risk_discussed'
                    cumulative_score += completed_fields(medicine)

    elif model_instance.__class__.__name__ == "Registration":
        # also need to count associate record in Site
        if Site.objects.filter(
            case=model_instance.case,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
        ).exists():
            cumulative_score += 1

    return cumulative_score
