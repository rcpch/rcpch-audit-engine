"""
Constants file to be referenced from the `recalculate_form_generate_response` function and its helper functions.
"""

from dataclasses import dataclass


@dataclass
class MinimumScorableFieldsForModel:
    """
    Used for `scoreable_fields_for_model_class_name`
    """

    model_name: str
    all_fields: list


Registration_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Registration",
    [
        "first_paediatric_assessment_date",
        "eligibility_criteria_met",
    ],
)

EpilepsyContext_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "EpilepsyContext",
    [
        "previous_febrile_seizure",
        "previous_acute_symptomatic_seizure",
        "is_there_a_family_history_of_epilepsy",
        "previous_neonatal_seizures",
        "diagnosis_of_epilepsy_withdrawn",
        "were_any_of_the_epileptic_seizures_convulsive",
        "experienced_prolonged_generalized_convulsive_seizures",
        "experienced_prolonged_focal_seizures",
    ],
)

FirstPaediatricAssessment_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "FirstPaediatricAssessment",
    [
        "first_paediatric_assessment_in_acute_or_nonacute_setting",
        "has_number_of_episodes_since_the_first_been_documented",
        "general_examination_performed",
        "neurological_examination_performed",
        "developmental_learning_or_schooling_problems",
        "behavioural_or_emotional_problems",
    ],
)

# minimum fields in multiaxial_diagnosis include:
# at least one episode that is epileptic fully completed
MultiaxialDiagnosis_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "MultiaxialDiagnosis",
    [
        "syndrome_present",
        "epilepsy_cause_known",
        "relevant_impairments_behavioural_educational",
        "autistic_spectrum_disorder",
        "global_developmental_delay_or_learning_difficulties",
        "mental_health_screen",
        "mental_health_issue_identified",
    ],
)

# returns minimum number of fields that could be scored for an epileptic episode
Episode_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Episode",
    [
        "seizure_onset_date",
        "seizure_onset_date_confidence",
        "episode_definition",
        "has_description_of_the_episode_or_episodes_been_gathered",  # deprecated as per #1015
        "epilepsy_or_nonepilepsy_status",
    ],
)

Syndrome_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Syndrome",
    [
        "syndrome_diagnosis_date",
        "syndrome__syndrome_name",
    ],
)

Comorbidity_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Comorbidity",
    [
        "comorbidity_diagnosis_date",
        "comorbidity__comorbidityentity__conceptId",
    ],
)

Assessment_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Assessment",
    [
        "childrens_epilepsy_surgical_service_referral_criteria_met",
        "consultant_paediatrician_referral_made",
        "paediatric_neurologist_referral_made",
        "childrens_epilepsy_surgical_service_referral_made",
        "epilepsy_specialist_nurse_referral_made",
    ],
)

Investigations_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Investigations",
    [
        "eeg_indicated",
        "twelve_lead_ecg_status",
        "ct_head_scan_status",
        "mri_indicated",
    ],
)

Management_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "Management",
    [
        "has_an_aed_been_given",
        "has_rescue_medication_been_prescribed",
        "individualised_care_plan_in_place",
        "has_been_referred_for_mental_health_support",
        "has_support_for_mental_health_support",
    ],
)

AntiEpilepsyMedicine_minimum_scorable_fields = MinimumScorableFieldsForModel(
    "AntiEpilepsyMedicine",
    [
        "medicine_name",
        "antiepilepsy_medicine_start_date",
        "antiepilepsy_medicine_risk_discussed",
    ],
)
