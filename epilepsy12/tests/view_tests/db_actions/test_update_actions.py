"""
# Epilepsy12Users
    [] Assert user can change user title
    [] Assert user can change user first_name
    [] Assert user can change user surname
    [] Assert user can change user email
    [] Assert user can change user role
    [] Assert user can resend create_user email
    

# Cases
    [] Assert user can change child first_name
    [] Assert user can change child surname
    [] Assert user can change child date_of_birth
    [] Assert user can change child sex
    [] Assert user can change child postcode
    [] Assert user can change child postcode to unknown
    [] Assert user can change child postcode to address unspecified
    [] Assert user can change child postcode to no fixed abode
    [] Assert user can change child nhs_number
    [] Assert user can change child ethnicity
    [] Assert user can opt child out of Epilepsy12
    

# First Paediatric Assessment
    for field in fields: [
        'first_paediatric_assessment_in_acute_or_nonacute_setting', single_choice_multiple_toggle_button
        'has_number_of_episodes_since_the_first_been_documented',   toggle_button
        'general_examination_performed',                            toggle_button
        'neurological_examination_performed',                       toggle_button
        'developmental_learning_or_schooling_problems',             toggle_button
        'behavioural_or_emotional_problems'                         toggle_button
    ]
    [] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to acute (CHRONICITY[0][0]==1)
    [] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to non-acute (CHRONICITY[0][0]==2)
    [] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to don't know (CHRONICITY[0][0]==3)
    [] Assert user can change 'has_number_of_episodes_since_the_first_been_documented' to True
    [] Assert user can change 'has_number_of_episodes_since_the_first_been_documented' to False
    [] Assert user can change 'general_examination_performed' to True
    [] Assert user can change 'general_examination_performed' to False
    [] Assert user can change 'neurological_examination_performed' to True
    [] Assert user can change 'neurological_examination_performed' to False
    [] Assert user can change 'developmental_learning_or_schooling_problems' to True
    [] Assert user can change 'developmental_learning_or_schooling_problems' to False
    [] Assert user can change 'behavioural_or_emotional_problems' to True
    [] Assert user can change 'behavioural_or_emotional_problems' to False
    
# Epilepsy Context
    for field in fields: [
        'previous_febrile_seizure',                                 single_choice_multiple_toggle_button 
        'previous_acute_symptomatic_seizure',                       single_choice_multiple_toggle_button
        'is_there_a_family_history_of_epilepsy',                    single_choice_multiple_toggle_button
        'previous_neonatal_seizures',                               toggle_button
        'were_any_of_the_epileptic_seizures_convulsive',            toggle_button
        'experienced_prolonged_generalized_convulsive_seizures',    single_choice_multiple_toggle_button
        'experienced_prolonged_focal_seizures',                     single_choice_multiple_toggle_button
        'diagnosis_of_epilepsy_withdrawn',                          toggle_button
    ]

    [] Assert user can change 'previous_febrile_seizure' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'previous_febrile_seizure' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'previous_febrile_seizure' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'previous_acute_symptomatic_seizure' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'previous_acute_symptomatic_seizure' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'previous_acute_symptomatic_seizure' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'is_there_a_family_history_of_epilepsy' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'is_there_a_family_history_of_epilepsy' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'is_there_a_family_history_of_epilepsy' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'previous_neonatal_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'previous_neonatal_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'previous_neonatal_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'were_any_of_the_epileptic_seizures_convulsive' to True
    [] Assert user can change 'were_any_of_the_epileptic_seizures_convulsive' to False
    [] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'experienced_prolonged_focal_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [] Assert user can change 'experienced_prolonged_focal_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [] Assert user can change 'experienced_prolonged_focal_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [] Assert user can change 'diagnosis_of_epilepsy_withdrawn' to True
    [] Assert user can change 'diagnosis_of_epilepsy_withdrawn' to False



# Multiaxial Diagnosis
    for field in fields: [
        'epilepsy_cause_known',                                         toggle_button
        'epilepsy_cause',                                               select
        'epilepsy_cause_categories',                                    multiple_choice_multiple_toggle_button
        'relevant_impairments_behavioural_educational',                 toggle_button
        'mental_health_screen',                                         toggle_button
        'mental_health_issue_identified',                               toggle_button
        'mental_health_issue',                                          single_choice_multiple_toggle_button
        'global_developmental_delay_or_learning_difficulties',          toggle_button
        'global_developmental_delay_or_learning_difficulties_severity', single_choice_multiple_toggle_button
        'autistic_spectrum_disorder',                                   toggle_button
    ]

    [] Assert user can change 'epilepsy_cause_known' to True
    [] Assert user can change 'epilepsy_cause_known' to False
    [] Assert user can change 'epilepsy_cause' to Aicardi's Syndrome (pk=135)
    [] Assert user can change 'epilepsy_cause_categories' to array of EPILEPSY_CAUSES[0][0]=='Gen' and EPILEPSY_CAUSES[1][0]=='Imm' and and EPILEPSY_CAUSES[5][0]=='Othe'
    [] Assert user can change 'epilepsy_cause_categories' to array of EPILEPSY_CAUSES[2][0]=='Inf' and EPILEPSY_CAUSES[3][0]=='Met' and EPILEPSY_CAUSES[4][0]=='Str'
    [] Assert user can change 'relevant_impairments_behavioural_educational' to True
    [] Assert user can change 'relevant_impairments_behavioural_educational' to False
    [] Assert user can change 'mental_health_screen' to True
    [] Assert user can change 'mental_health_screen' to False
    [] Assert user can change 'mental_health_issue_identified' to True
    [] Assert user can change 'mental_health_issue_identified' to False
    [] Assert user can change 'autistic_spectrum_disorder' to True
    [] Assert user can change 'autistic_spectrum_disorder' to False
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties' to True
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties' to False
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[0][0]=='mild'
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[1][0]=='moderate'
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[2][0]=='severe'
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[3][0]=='profound'
    [] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[4][0]=='uncertain'

# Episode
    for field in fields: [
        'seizure_onset_date',                                                date_field
        'seizure_onset_date_confidence',                                     single_choice_multiple_toggle_button
        'episode_definition',                                                select
        'has_description_of_the_episode_or_episodes_been_gathered',          toggle_button
        'edit_description',                                                  string - updated in view function
        'delete_description_keyword',                                        Keyword id - updated in view function
        'epilepsy_or_nonepilepsy_status',                                    single_choice_multiple_toggle_button
        'epileptic_seizure_onset_type',                                      single_choice_multiple_toggle_button
        'focal_onset_epilepsy_checked_changed',                              updated in view function
        'epileptic_generalised_onset',                                       single_choice_multiple_toggle_button
        'nonepilepsy_generalised_onset',                                     single_choice_multiple_toggle_button
        'nonepileptic_seizure_type',                                         select
        'nonepileptic_seizure_subtype',                                      select
    ]
    [] Assert user can change 'seizure_onset_date' to today
    [] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[0][0]=='Apx' (Approximate)
    [] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[1][0]=='Exc' (Exact)
    [] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[2][0]=='NK' (Not Known)
    [] Assert user can change 'episode_definition' to EPISODE_DEFINITION[0][0]=='a' ('This was a single episode')
    [] Assert user can change 'episode_definition' to EPISODE_DEFINITION[1][0]=='b' ('This was a cluster within 24 hours')
    [] Assert user can change 'episode_definition' to EPISODE_DEFINITION[2][0]=='c' ('These were 2 or more episodes more than 24 hours apart')
    [] Assert user can change 'has_description_of_the_episode_or_episodes_been_gathered' to True
    [] Assert user can delete 'gelastic' in 'delete_description_keyword' from ['gelastic', 'left']
    [] Assert user can change 'edit_description' to "Jacob fell to the floor and shook the left side of his body."
    [] Assert user can change 'edit_description' to "Jacob fell to the floor and shook the left side of his body."
    [] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[0][0]=='E' (Epilepsy)
    [] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[1][0]=='NE' (Epilepsy)
    [] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[2][0]=='U' (Uncertain)
    [] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[0][0]=='FO' (Focal Onset)
    [] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[1][0]=='GO' (Generalised Onset)
    [] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[2][0]=='UO' (Unknown Onset)
    [] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[3][0]=='UC' (Unclassified)
    [] Assert user can change 'focal_onset_epilepsy_checked_changed' to ........
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[0][0]=='AEM' ('Absence with eyelid myoclonia')
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[1][0]=='Ato' ('Atonic')]], tuple[Literal['Aab'], Literal['Atypical absence']], tuple[Literal['Clo'], Literal['Clonic']], tuple[Literal['EpS'], Literal['Epileptic spasms']], tuple[Literal['MyC'], Literal['Myoclonic']], tuple[Literal['MAb'], Literal['Myoclonic absence']], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[2][0]=='Aab' ('Atypical absence')]], tuple[Literal['Clo'], Literal['Clonic']], tuple[Literal['EpS'], Literal['Epileptic spasms']], tuple[Literal['MyC'], Literal['Myoclonic']], tuple[Literal['MAb'], Literal['Myoclonic absence']], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[3][0]=='Clo' ('Clonic')]], tuple[Literal['EpS'], Literal['Epileptic spasms']], tuple[Literal['MyC'], Literal['Myoclonic']], tuple[Literal['MAb'], Literal['Myoclonic absence']], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[4][0]=='EpS' ('Epileptic spasms')]], tuple[Literal['MyC'], Literal['Myoclonic']], tuple[Literal['MAb'], Literal['Myoclonic absence']], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[5][0]=='MyC' ('Myoclonic')]], tuple[Literal['MAb'], Literal['Myoclonic absence']], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[6][0]=='MAb' ('Myoclonic absence')]], tuple[Literal['MTC'], Literal['Myoclonic-tonic-clonic']], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[7][0]=='MTC' ('Myoclonic-tonic-clonic')]], tuple[Literal['MAt'], Literal['Myoclonic-atonic']], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[8][0]=='MAt' ('Myoclonic-atonic')]], tuple[Literal['Ton'], Literal['Tonic']], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[9][0]=='Ton' ('Tonic')]], tuple[Literal['TCl'], Literal['Tonic-clonic']], tuple[Literal['TAb'], Literal['Typical absence']], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[10][0]=='TCl' ('Tonic-clonic')
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[11][0]=='TAb' ('Typical absence')
    [] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[12][0]=='Oth' ('Other')
    [] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[0][0]=='BAr' ('Behaviour arrest')
    [] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[1][0]=='EpS' ('Epileptic spasms')
    [] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[2][0]=='TCl' ('Tonic-clonic')
    [] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[3][0]=='Oth' ('Other')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[0][0]=='BPP' ('Behavioral Psychological And Psychiatric Disorders')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[1][0]=='MAD' ('Migraine Associated Disorders')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[2][0]=='ME' ('Miscellaneous Events')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[3][0]=='SRC' ('Sleep Related Conditions')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[4][0]=='SAS' ('Syncope And Anoxic Seizures')
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[5][0]=='PMD' ('Paroxysmal Movement Disorders')]], tuple[Literal['Oth'], Literal['Other']]]
    [] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[6][0]=='Oth' ('Other')

    
    [] Assert user cannot change 'seizure_onset_date' to before Case.date_of_birth (raise ValidationError)
    [] Assert user cannot change 'seizure_onset_date' to before Registration.registration_date (raise ValidationError)
    [] Assert user cannot change 'seizure_onset_date' to future date (raise ValidationError)
    

# Comorbidity
    for field in fields: [
        'comorbidity_diagnosis_date',                                       date_field
        'comorbidity_diagnosis',                                            select
    ]
    [] Assert user can change
    

# Assessment
    for field in fields: [
        'consultant_paediatrician_referral_made',                               toggle_button
        'consultant_paediatrician_referral_date',                               date_field
        'consultant_paediatrician_input_date',                                  date_field
        'general_paediatric_centre',                                            button click
        'edit_general_paediatric_centre',                                       button click
        'update_general_paediatric_centre_pressed',                             button click (action:edit/cancel)
        'paediatric_neurologist_referral_made',                                 toggle_button
        'paediatric_neurologist_referral_date',                                 date_field
        'paediatric_neurologist_input_date',                                    date_field
        'paediatric_neurology_centre',                                          button click
        'edit_paediatric_neurology_centre',                                     button click    
        'update_paediatric_neurology_centre_pressed',                           button click (action:edit/cancel)
        'childrens_epilepsy_surgical_service_referral_criteria_met',            toggle_button                
        'childrens_epilepsy_surgical_service_referral_made',                    toggle_button        
        'childrens_epilepsy_surgical_service_referral_date',                    date_field    
        'childrens_epilepsy_surgical_service_input_date',                       date_field
        'epilepsy_surgery_centre',                                              button click
        'edit_epilepsy_surgery_centre',                                         button click
        'update_epilepsy_surgery_centre_pressed',                               button click (action:edit/cancel)            
        'epilepsy_specialist_nurse_referral_made',                              toggle_button
        'epilepsy_specialist_nurse_referral_date',                              date_field    
        'epilepsy_specialist_nurse_input_date',                                 date_field
    ]
    [] Assert user can change

# Investigations
    for field in fields: [
        'eeg_indicated',                                                        toggle_button
        'eeg_request_date',                                                     date_field
        'eeg_performed_date',                                                   date_field    
        'eeg_declined',                                                         button click (confirm:edit/decline)
        'twelve_lead_ecg_status',                                               toggle_button        
        'ct_head_scan_status',                                                  toggle_button    
        'mri_indicated',                                                        toggle_button
        'mri_brain_requested_date',                                             date_field
        'mri_brain_reported_date',                                              date_field
        'mri_brain_declined',                                                   button click (confirm:edit/decline)
    ]
    [] Assert user can change

# Management
    for field in fields: [
        'individualised_care_plan_in_place',                                    toggle_button
        'individualised_care_plan_date',                                        date_field
        'individualised_care_plan_has_parent_carer_child_agreement',            toggle_button
        'individualised_care_plan_includes_service_contact_details',            toggle_button
        'individualised_care_plan_include_first_aid',                           toggle_button
        'individualised_care_plan_parental_prolonged_seizure_care',             toggle_button
        'individualised_care_plan_includes_general_participation_risk',         toggle_button
        'individualised_care_plan_addresses_water_safety',                      toggle_button
        'individualised_care_plan_addresses_sudep',                             toggle_button    
        'individualised_care_plan_includes_ehcp',                               toggle_button    
        'has_individualised_care_plan_been_updated_in_the_last_year',           toggle_button                        
        'has_been_referred_for_mental_health_support',                          toggle_button        
        'has_support_for_mental_health_support',                                toggle_button
        'has_an_aed_been_given',                                                toggle_button
        'has_rescue_medication_been_prescribed',                                toggle_button
    ]
    [] Assert user can change

# Antiepilepsy Medicine
    for field in fields: [
        'edit_antiepilepsy_medicine',                                           button click (antiepilepsy_medicine_id)
        'medicine_id',                                                          post on select change handled in view
        'antiepilepsy_medicine_start_date',                                     date_field
        'antiepilepsy_medicine_add_stop_date',                                  button click (antiepilepsy_medicine_id)
        'antiepilepsy_medicine_remove_stop_date',                               button click (antiepilepsy_medicine_id)
        'antiepilepsy_medicine_stop_date',                                      date_field
        'antiepilepsy_medicine_risk_discussed',                                 toggle_button
        'is_a_pregnancy_prevention_programme_in_place',                         toggle_button
        'has_a_valproate_annual_risk_acknowledgement_form_been_completed',      toggle_button
    ]
    [] Assert user can change


"""
# Python imports
from datetime import date

# Django imports
from django.urls import reverse

# third party imports
import pytest
import factory

# E12 imports
from epilepsy12.tests.UserDataClasses import (
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.factories import (
    E12UserFactory,
    E12CaseFactory,
    E12RegistrationFactory,
    E12SiteFactory,
    E12AntiEpilepsyMedicineFactory,
)

# E12 imports
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
    Episode,
    Keyword,
    EpilepsyCauseEntity,
    MultiaxialDiagnosis,
    ComorbidityEntity,
    Comorbidity,
    MedicineEntity,
    AntiEpilepsyMedicine,
)

from epilepsy12.constants import VALID_NHS_NUMS, SEX_TYPE, CHRONICITY
from epilepsy12.general_functions import generate_nhs_number


@pytest.mark.skip(reason="Unfinished test. Very much still a work in progress.")
@pytest.mark.django_db
def test_user_updates_first_paediatric_assessment_in_acute_or_nonacute_setting_success(
    client, seed_groups_fixture, seed_users_fixture, seed_cases_fixture
):
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    registration = factory.RelatedFactory(
        E12RegistrationFactory,
        factory_related_name="case",
    )
    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}",
        nhs_number=generate_nhs_number(),
        sex=SEX_TYPE[0][0],
        registration=registration,  # ensure related audit factories not generated
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, item in enumerate(CHRONICITY):
        client.post(
            reverse(
                "first_paediatric_assessment_in_acute_or_nonacute_setting",
                kwargs={
                    "first_paediatric_assessment_id": CASE_FROM_TEST_USER_ORGANISATION.registration.firstpaediatricassessment.id,
                },
            ),
            headers={"Hx-Trigger-Name": item[0], "Hx-Request": "true"},
        )
        validate_single_choice_multiple_toggle_button(
            field_name="first_paediatric_assessment_in_acute_or_nonacute_setting",
            model_instance=CASE_FROM_TEST_USER_ORGANISATION.registration.firstpaediatricassessment,
            expected_result=item[0],
            assert_pass=True,
        )


# Test helper methods - there is one for each page_element
def validate_date_assertions(
    field_name: str,
    model_instance,
    case,
    second_date: date = None,
    is_initial_date=False,
    assert_pass=True,
):
    """
    Tests all dates
    """

    date_to_test: date = getattr(model_instance, field_name, None)

    if date_to_test is None or type(date_to_test) is not date:
        raise Exception("This field either does not exist or is not a date.")

    if assert_pass:
        assert (
            date_to_test <= date.today()
        ), f"{field_name} - {date_to_test} is not in the future - Expected PASS"
        assert (
            date_to_test >= case.date_of_birth
        ), f"{field_name} - {date_to_test} is not before {case}'s date of birth - Expected PASS"
        assert (
            date_to_test >= case.registration.registration_date
        ), f"{date_to_test} is not before {case}'s first paediatric assessment date ({case.registration.registration_date}) - Expected PASS"
    else:
        assert (
            date_to_test > date.today()
        ), f"{field_name} - {date_to_test} is in the future - Expected FAIL"
        assert (
            date_to_test < case.date_of_birth
        ), f"{field_name} - {date_to_test} is before {case}'s date of birth - Expected FAIL"
        assert (
            date_to_test < case.registration.registration_date
        ), f"{field_name} - {date_to_test} is before {case}'s first paediatric assessment date ({case.registration.registration_date}) - Expected FAIL"

    if second_date is not None:
        if assert_pass:
            if is_initial_date:
                assert (
                    date_to_test <= second_date
                ), f"{field_name} - {date_to_test} is before {second_date} - Expected PASS"
            else:
                assert (
                    date_to_test >= second_date
                ), f"{field_name} - {date_to_test} is after {second_date} - Expected PASS"
        else:
            if is_initial_date:
                assert (
                    date_to_test > second_date
                ), f"{field_name} - {date_to_test} is not before {second_date} - Expected FAIL"
            else:
                assert (
                    date_to_test < second_date
                ), f"{field_name} - {date_to_test} is not after {second_date} - Expected FAIL"


def validate_toggle_button(
    field_name: str, model_instance, expected_result: bool, assert_pass=True
):
    """
    Asserts whether the result stored in the model matches that expected
    """
    field_value = getattr(model_instance, field_name, None)

    if field_value is not None:
        if assert_pass:
            assert (
                expected_result == field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected PASS"
        else:
            assert (
                expected_result != field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected Fail"


def validate_single_choice_multiple_toggle_button(
    field_name: str, model_instance, expected_result, assert_pass=True
):
    """
    Asserts whether the result stored in the model matches that expected
    """
    field_value = getattr(model_instance, field_name, None)

    if field_value is not None:
        if assert_pass:
            assert (
                expected_result == field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected PASS"
        else:
            assert (
                expected_result != field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected Fail"
