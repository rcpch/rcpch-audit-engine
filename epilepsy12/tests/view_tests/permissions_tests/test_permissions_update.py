"""
## Update Tests

# Epilepsy12Users
    [x] Assert an Audit Centre Administrator CANNOT update users inside own Trust
    [x] Assert an Audit Centre Administrator CANNOT update users from outside own Trust 
    [x] Assert an audit centre clinician CANNOT update users inside own Trust
    [x] Assert an audit centre clinician CANNOT update users from outside own Trust 
    [x] Assert an Audit Centre Lead Clinician CANNOT update users outside own Trust

    [x] Assert an Audit Centre Lead Clinician can update users inside own Trust
    [x] Assert RCPCH Audit Team can update users in any trust
    [x] Assert Clinical Audit Team can update users in own trust
    [x] Assert Clinical Audit Team can update users in different trusts

# Cases
    [x] Assert an Audit Centre Administrator CANNOT update patient records outside own Trust
    [x] Assert an audit centre clinician CANNOT update patient records outside own Trust
    [x] Assert an Audit Centre Lead Clinician CANNOT update patient records outside own Trust

    [x] Assert an Audit Centre Administrator CAN update patient records inside own Trust
    [x] Assert an audit centre clinician can update patient records within own organisation
    [x] Assert an Audit Centre Lead Clinician can update patient records within own Trust
    [x] Assert RCPCH Audit Team can update patient records within an organisation
    [x] Assert Clinical Audit Team can update patient records within an organisation

# First Paediatric Assessment
    for field in fields: [
        'first_paediatric_assessment_in_acute_or_nonacute_setting',
        'has_number_of_episodes_since_the_first_been_documented',
        'general_examination_performed',
        'neurological_examination_performed',
        'developmental_learning_or_schooling_problems',
        'behavioural_or_emotional_problems'
    ]
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

# Epilepsy Context
    for field in fields: [
        'previous_febrile_seizure',                                 single_choice_multiple_toggle_button
        'previous_acute_symptomatic_seizure',                       single_choice_multiple_toggle_button
        'is_there_a_family_history_of_epilepsy',                    toggle_button
        'previous_neonatal_seizures',                               single_choice_multiple_toggle_button
        'were_any_of_the_epileptic_seizures_convulsive',            toggle_button
        'experienced_prolonged_generalized_convulsive_seizures',    single_choice_multiple_toggle_button
        'experienced_prolonged_focal_seizures',                     single_choice_multiple_toggle_button
        'diagnosis_of_epilepsy_withdrawn',                          toggle_button
    ]

    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK


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

    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

# Episode
    for field in fields: [
        seizure_onset_date',                                                date_field
        seizure_onset_date_confidence',                                     single_choice_multiple_toggle_button
        episode_definition',                                                select
        has_description_of_the_episode_or_episodes_been_gathered',          toggle_button
        edit_description',                                                  string - updated in view function
        delete_description_keyword',                                        Keyword id - updated in view function
        epilepsy_or_nonepilepsy_status',                                    single_choice_multiple_toggle_button
        epileptic_seizure_onset_type',                                      single_choice_multiple_toggle_button
        focal_onset_epilepsy_checked_changed',                              updated in view function
        epileptic_generalised_onset',                                       single_choice_multiple_toggle_button
        nonepilepsy_generalised_onset',                                     single_choice_multiple_toggle_button
        nonepileptic_seizure_type',                                         select
        nonepileptic_seizure_subtype',                                      select
    ]
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

# Comorbidity
    for field in fields: [
        'comorbidity_diagnosis_date',                                       date_field
        'comorbidity_diagnosis',                                            select
    ]
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

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
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

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
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

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
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK

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
    [x] Assert an Audit Centre Administrator cannot change 'field' inside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    
    [x] Assert an Audit Centre Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can change 'field' - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can change 'field' - response.status_code == HTTPStatus.OK


"""
# python imports
import pytest
from http import HTTPStatus
from datetime import date

# django imports
from django.urls import reverse
from django.contrib.auth.models import Group

import factory

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
)
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_clinicial_audit_team_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.factories import (
    E12UserFactory,
    E12SiteFactory,
    E12AntiEpilepsyMedicineFactory,
)


@pytest.mark.django_db
def test_users_update_users_forbidden(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """
    Simulating different E12 Users attempting to update users in Epilepsy12

    Assert these users cannot change Epilepsy12Users
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    # Seed Test user to be updated
    USER_FROM_DIFFERENT_ORG = E12UserFactory(
        email=f"{DIFF_TRUST_DIFF_ORGANISATION}_ADMINISTRATOR@email.com",
        first_name=f"{DIFF_TRUST_DIFF_ORGANISATION}_ADMINISTRATOR",
        role=test_user_audit_centre_administrator_data.role,
        # Assign flags based on user role
        is_active=test_user_audit_centre_administrator_data.is_active,
        is_staff=test_user_audit_centre_administrator_data.is_staff,
        is_rcpch_audit_team_member=test_user_audit_centre_administrator_data.is_rcpch_audit_team_member,
        is_rcpch_staff=test_user_audit_centre_administrator_data.is_rcpch_staff,
        organisation_employer=TEST_USER_ORGANISATION,
        groups=[
            Group.objects.get(name=test_user_audit_centre_administrator_data.group_name)
        ],
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        response = client.get(
            reverse(
                "edit_epilepsy12_user",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "epilepsy12_user_id": USER_FROM_DIFFERENT_ORG.id,
                },
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update user {USER_FROM_DIFFERENT_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"

        # These users can't update any users, including same Trust
        if test_user.first_name in [
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
        ]:
            response = client.get(
                reverse(
                    "edit_epilepsy12_user",
                    kwargs={
                        "organisation_id": TEST_USER_ORGANISATION.id,
                        "epilepsy12_user_id": test_user.id,
                    },
                )
            )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update user {test_user} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_users_success(
    client,
):
    """
    Simulating different E12 Users attempting to update users in Epilepsy12

    Assert these users are allowed to change Epilepsy12Users
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    USER_FROM_DIFFERENT_ORG = E12UserFactory(
        email=f"{DIFF_TRUST_DIFF_ORGANISATION}_ADMINISTRATOR@email.com",
        first_name=f"{DIFF_TRUST_DIFF_ORGANISATION}_ADMINISTRATOR",
        role=test_user_audit_centre_administrator_data.role,
        # Assign flags based on user role
        is_active=test_user_audit_centre_administrator_data.is_active,
        is_staff=test_user_audit_centre_administrator_data.is_staff,
        is_rcpch_audit_team_member=test_user_audit_centre_administrator_data.is_rcpch_audit_team_member,
        is_rcpch_staff=test_user_audit_centre_administrator_data.is_rcpch_staff,
        organisation_employer=DIFF_TRUST_DIFF_ORGANISATION,
        groups=[
            Group.objects.get(name=test_user_audit_centre_administrator_data.group_name)
        ],
    )

    selected_users = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]

    users = Epilepsy12User.objects.filter(first_name__in=selected_users)

    if len(users) != len(selected_users):
        assert (
            False
        ), f"Incorrect number of users selected. Requested {len(selected_users)} but queryset contains {len(users)}"

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        response = client.get(
            reverse(
                "edit_epilepsy12_user",
                kwargs={
                    "organisation_id": TEST_USER_ORGANISATION.id,
                    "epilepsy12_user_id": test_user.id,
                },
            )
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update user {test_user} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"

        if test_user.first_name in [
            test_user_rcpch_audit_team_data,
            test_user_clinicial_audit_team_data,
        ]:
            response = client.get(
                reverse(
                    "edit_epilepsy12_user",
                    kwargs={
                        "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                        "epilepsy12_user_id": USER_FROM_DIFFERENT_ORG.id,
                    },
                )
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update user {USER_FROM_DIFFERENT_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_cases_forbidden(
    client,
):
    """
    Simulating different E12 Users attempting to update cases in Epilepsy12

    Assert these users cannot change cases
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        response = client.get(
            reverse(
                "update_case",
                kwargs={
                    "organisation_id": TEST_USER_ORGANISATION.id,
                    "case_id": CASE_FROM_DIFF_ORG.id,
                },
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update case {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_cases_success(
    client,
):
    """
    Simulating different E12 Users attempting to update cases in Epilepsy12

    Assert these users can change cases
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
            test_user_rcpch_audit_team_data.role_str,
        ]
    )

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        response = client.get(
            reverse(
                "update_case",
                kwargs={
                    "organisation_id": TEST_USER_ORGANISATION.id,
                    "case_id": CASE_FROM_SAME_ORG.id,
                },
            )
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update case {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_first_paediatric_assessment_forbidden(client):
    """
    Simulating different E12 Users attempting to update first paediatric assessment in Epilepsy12

    Assert these users cannot change first paediatric assessment
    """

    # set up constants
    # GOSH

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "first_paediatric_assessment_in_acute_or_nonacute_setting",
        "has_number_of_episodes_since_the_first_been_documented",
        "general_examination_performed",
        "neurological_examination_performed",
        "developmental_learning_or_schooling_problems",
        "behavioural_or_emotional_problems",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for url in URLS:
            response = client.get(
                reverse(
                    url,
                    kwargs={
                        "first_paediatric_assessment_id": CASE_FROM_DIFF_ORG.registration.firstpaediatricassessment.id,
                    },
                )
            )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update case {url} for {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_first_paediatric_assessment_success(client):
    """
    Simulating different E12 Users attempting to update first paediatric assessment in Epilepsy12

    Assert these users can change first paediatric assessment
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "first_paediatric_assessment_in_acute_or_nonacute_setting",
        "has_number_of_episodes_since_the_first_been_documented",
        "general_examination_performed",
        "neurological_examination_performed",
        "developmental_learning_or_schooling_problems",
        "behavioural_or_emotional_problems",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL == "first_paediatric_assessment_in_acute_or_nonacute_setting":
                # this is single_choice_multiple_toggle_button - select option 1
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "first_paediatric_assessment_id": CASE_FROM_SAME_ORG.registration.firstpaediatricassessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "1", "Hx-Request": "true"},
                )
            else:
                # all other options are toggle buttons: select True
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "first_paediatric_assessment_id": CASE_FROM_SAME_ORG.registration.firstpaediatricassessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-false", "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update first paediatric assessment ({URL}) for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_first_epilepsy_context_forbidden(client):
    """
    Simulating different E12 Users attempting to update epilepsy context in Epilepsy12

    Assert these users cannot change epilepsy context
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "previous_febrile_seizure",
        "previous_acute_symptomatic_seizure",
        "is_there_a_family_history_of_epilepsy",
        "previous_neonatal_seizures",
        "were_any_of_the_epileptic_seizures_convulsive",
        "experienced_prolonged_generalized_convulsive_seizures",
        "experienced_prolonged_focal_seizures",
        "diagnosis_of_epilepsy_withdrawn",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            response = client.get(
                reverse(
                    URL,
                    kwargs={
                        "epilepsy_context_id": CASE_FROM_DIFF_ORG.registration.epilepsycontext.id,
                    },
                )
            )

            assert (
                response.status_code == response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update epilepsy context {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_epilepsy_context_success(client):
    """
    Simulating different E12 Users attempting to update epilepsy context in Epilepsy12

    Assert these users can change epilepsy context
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "previous_febrile_seizure",
        "previous_acute_symptomatic_seizure",
        "is_there_a_family_history_of_epilepsy",
        "previous_neonatal_seizures",
        "were_any_of_the_epileptic_seizures_convulsive",
        "experienced_prolonged_generalized_convulsive_seizures",
        "experienced_prolonged_focal_seizures",
        "diagnosis_of_epilepsy_withdrawn",
    ]

    single_choice_multiple_toggle_fields = [
        "previous_febrile_seizure",
        "previous_acute_symptomatic_seizure",
        "is_there_a_family_history_of_epilepsy",
        "previous_neonatal_seizures",
        "experienced_prolonged_generalized_convulsive_seizures",
        "experienced_prolonged_focal_seizures",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in single_choice_multiple_toggle_fields:
                # this is single_choice_multiple_toggle_button - select option 1
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "epilepsy_context_id": CASE_FROM_SAME_ORG.registration.epilepsycontext.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "1", "Hx-Request": "true"},
                )
            else:
                # all other options are toggle buttons: select True
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "epilepsy_context_id": CASE_FROM_SAME_ORG.registration.epilepsycontext.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-false", "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update epilepsy context for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_first_multiaxial_diagnosis_forbidden(client):
    """
    Simulating different E12 Users attempting to update multiaxial diagnosis in Epilepsy12

    Assert these users cannot change multiaxial diagnosis
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "epilepsy_cause_known",
        "epilepsy_cause",
        "epilepsy_cause_categories",
        "relevant_impairments_behavioural_educational",
        "mental_health_screen",
        "mental_health_issue_identified",
        "mental_health_issue",
        "global_developmental_delay_or_learning_difficulties",
        "global_developmental_delay_or_learning_difficulties_severity",
        "autistic_spectrum_disorder",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            response = client.get(
                reverse(
                    URL,
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis.id,
                    },
                )
            )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update multiaxial diagnosis {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_multiaxial_diagnosis_success(client):
    """
    Simulating different E12 Users attempting to update multiaxial diagnosis in Epilepsy12

    Assert these users can change multiaxial diagnosis
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "epilepsy_cause_known",
        "epilepsy_cause",
        "epilepsy_cause_categories",
        "relevant_impairments_behavioural_educational",
        "mental_health_screen",
        "mental_health_issue_identified",
        "mental_health_issue",
        "global_developmental_delay_or_learning_difficulties",
        "global_developmental_delay_or_learning_difficulties_severity",
        "autistic_spectrum_disorder",
    ]

    toggle_fields = [
        "epilepsy_cause_known",
        "relevant_impairments_behavioural_educational",
        "mental_health_screen",
        "mental_health_issue_identified",
        "global_developmental_delay_or_learning_difficulties",
        "autistic_spectrum_disorder",
    ]

    single_choice_multiple_toggle_button_fields = [
        "mental_health_issue",
        "global_developmental_delay_or_learning_difficulties_severity",
    ]

    # select_fields = ["epilepsy_cause"] tested in separate function

    multiple_choice_multiple_toggle_button_fields = ["epilepsy_cause_categories"]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in toggle_fields:
                # all other options are toggle buttons: select True
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif (
                URL in single_choice_multiple_toggle_button_fields
                or URL in multiple_choice_multiple_toggle_button_fields
            ):
                # this is single_choice_multiple_toggle_button - select option 1
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.epilepsycontext.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "1", "Hx-Request": "true"},
                )
            else:
                # all other options are selects: select True
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "epilepsy_cause", "Hx-Request": "true"},
                    data={"epilepsy_cause": "179"},
                )

            assert (
                response.status_code == response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update epilepsy context for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_update_multiaxial_diagnosis_cause_success(client):
    """
    Assert different E12 Users can update Cause section of multiaxial diagnosis.

    Endpoint url names:

        'epilepsy_cause_known',
        'epilepsy_cause_categories',
        'epilepsy_cause'
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # Fryns macrocephaly
    EPILEPSY_CAUSE_ENTITY = EpilepsyCauseEntity.objects.get(id=179)

    for test_user in users:
        client.force_login(test_user)

        response_epilepsy_cause_known = client.post(
            reverse(
                "epilepsy_cause_known",
                kwargs={
                    "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id,
                },
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )

        assert (
            MultiaxialDiagnosis.objects.get(
                registration=CASE_FROM_SAME_ORG.registration
            ).epilepsy_cause_known
            is True
        ), f"{test_user} from {test_user.organisation_employer} attempted POST True to epilepsy_cause_known but model did not update."

        response_epilepsy_cause_categories = client.post(
            reverse(
                "epilepsy_cause_categories",
                kwargs={
                    "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id,
                },
            ),
            headers={"Hx-Trigger-Name": "Gen", "Hx-Request": "true"},
        )

        assert MultiaxialDiagnosis.objects.get(
            registration=CASE_FROM_SAME_ORG.registration
        ).epilepsy_cause_categories == [
            "Gen"
        ], f"{test_user} from {test_user.organisation_employer} attempted POST `Gen` to epilepsy_cause_categories but model did not update."

        response_epilepsy_cause = client.post(
            reverse(
                "epilepsy_cause",
                kwargs={
                    "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id,
                },
            ),
            headers={"Hx-Trigger-Name": "epilepsy_cause", "Hx-Request": "true"},
            data={"epilepsy_cause": f"{EPILEPSY_CAUSE_ENTITY.id}"},
        )

        assert (
            MultiaxialDiagnosis.objects.get(
                registration=CASE_FROM_SAME_ORG.registration
            ).epilepsy_cause
            == EPILEPSY_CAUSE_ENTITY
        ), f"{test_user} from {test_user.organisation_employer} attempted POST `epilepsy_cause:{EPILEPSY_CAUSE_ENTITY.id}` but MultiaxialDiagnosis model field did not update."

        # Reset answers for next User
        MultiaxialDiagnosis.objects.filter(
            registration=CASE_FROM_SAME_ORG.registration
        ).update(
            epilepsy_cause_known=None,
            epilepsy_cause_categories=[],
            epilepsy_cause=None,
        )


@pytest.mark.django_db
def test_users_update_episode_forbidden(client):
    """
    Simulating different E12 Users attempting to update episode in Epilepsy12

    Assert these users cannot change episode
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # Create objs to search for
    episode = Episode.objects.create(
        episode_definition="a",
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
    )

    URLS = [
        "seizure_onset_date",
        "seizure_onset_date_confidence",
        "episode_definition",
        "has_description_of_the_episode_or_episodes_been_gathered",
        "edit_description",
        "delete_description_keyword",
        "epilepsy_or_nonepilepsy_status",
        "epileptic_seizure_onset_type",
        "focal_onset_epilepsy_checked_changed",
        "epileptic_generalised_onset",
        "nonepilepsy_generalised_onset",
        "nonepileptic_seizure_type",
        "nonepileptic_seizure_subtype",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL == "delete_description_keyword":
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                            "description_keyword_id": Keyword.objects.all().first().id,
                        },
                    )
                )
            else:
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    )
                )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update episode {URL} for  {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_episode_success(client):
    """
    Simulating different E12 Users attempting to update episode in Epilepsy12

    Assert these users can change episode
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    date_fields = ["seizure_onset_date"]

    toggle_fields = ["has_description_of_the_episode_or_episodes_been_gathered"]

    single_choice_multiple_toggle_button_fields = [
        "seizure_onset_date_confidence",
        "epilepsy_or_nonepilepsy_status",
        "epileptic_seizure_onset_type",
        "epileptic_generalised_onset",
        "nonepilepsy_generalised_onset",
    ]

    select_fields = [
        "episode_definition",
        "nonepileptic_seizure_type",
        "nonepileptic_seizure_subtype",
    ]

    # Create objs to search for
    episode = Episode.objects.create(
        episode_definition="a",
        multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
    )

    URLS = [
        "seizure_onset_date",
        "seizure_onset_date_confidence",
        "episode_definition",
        "has_description_of_the_episode_or_episodes_been_gathered",
        "edit_description",
        "delete_description_keyword",
        "epilepsy_or_nonepilepsy_status",
        "epileptic_seizure_onset_type",
        "focal_onset_epilepsy_checked_changed",
        "epileptic_generalised_onset",
        "nonepilepsy_generalised_onset",
        "nonepileptic_seizure_type",
        "nonepileptic_seizure_subtype",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL == "delete_description_keyword":
                keyword = Keyword.objects.all().first()
                description_keyword_list = [keyword.keyword]
                episode.description_keywords = description_keyword_list
                episode.save()

                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                            "description_keyword_id": 0,  # remove first item in list
                        },
                    )
                )
            elif URL in single_choice_multiple_toggle_button_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "1", "Hx-Request": "true"},
                )
            elif URL in toggle_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif URL in select_fields:
                post_body = None
                if URL == "episode_definition":
                    post_body = "a"
                elif URL == "nonepileptic_seizure_type":
                    post_body = "MAD"
                elif URL == "nonepileptic_seizure_subtype":
                    post_body = "c"
                else:
                    raise ValueError("No select chosen")
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: post_body},
                )
            elif URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            elif URL == "edit_description":
                # remaining values are strings
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "description", "Hx-Request": "true"},
                    data={"description": "This is a description"},
                )
            else:
                # this is the choice for focal epilepsy
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "episode_id": episode.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "LATERALITY", "Hx-Request": "true"},
                    data={URL: "focal_onset_left"},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update episode {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_comorbidity_forbidden(client):
    """
    Simulating different E12 Users attempting to update comorbidity in Epilepsy12

    Assert these users cannot change comorbidity
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "comorbidity_diagnosis_date",
        "comorbidity_diagnosis",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            comorbidity, created = Comorbidity.objects.update_or_create(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
                comorbidity_diagnosis_date=date.today(),
                comorbidityentity=ComorbidityEntity.objects.all().first(),
            )
            comorbidity.save()

            if URL == "comorbidity_diagnosis_date":
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "comorbidity_id": comorbidity.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            elif URL == "comorbidity_diagnosis":
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "comorbidity_id": comorbidity.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: ComorbidityEntity.objects.all().first().id},
                )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update comorbidity {URL} for {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_comorbidity_success(client):
    """
    Simulating different E12 Users attempting to update comorbidity in Epilepsy12

    Assert these users can change comorbidity
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "comorbidity_diagnosis_date",
        "comorbidity_diagnosis",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            comorbidity, created = Comorbidity.objects.update_or_create(
                multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
                comorbidity_diagnosis_date=date.today(),
                comorbidityentity=ComorbidityEntity.objects.all().first(),
            )
            comorbidity.save()

            if URL == "comorbidity_diagnosis_date":
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "comorbidity_id": comorbidity.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            elif URL == "comorbidity_diagnosis":
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "comorbidity_id": comorbidity.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: ComorbidityEntity.objects.all().first().id},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update comorbidities {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_assessment_forbidden(client):
    """
    Simulating different E12 Users attempting to update assessment in Epilepsy12

    Assert these users cannot change assessment
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields

    toggle_buttons = [
        "consultant_paediatrician_referral_made",
        "paediatric_neurologist_referral_made",
        "childrens_epilepsy_surgical_service_referral_criteria_met",
        "childrens_epilepsy_surgical_service_referral_made",
        "epilepsy_specialist_nurse_referral_made",
    ]

    date_fields = [
        "consultant_paediatrician_referral_date",
        "consultant_paediatrician_input_date",
        "paediatric_neurologist_referral_date",
        "paediatric_neurologist_input_date",
        "childrens_epilepsy_surgical_service_referral_date",
        "childrens_epilepsy_surgical_service_input_date",
        "epilepsy_specialist_nurse_referral_date",
        "epilepsy_specialist_nurse_input_date",
    ]

    URLS = [
        "consultant_paediatrician_referral_made",
        "consultant_paediatrician_referral_date",
        "consultant_paediatrician_input_date",
        "general_paediatric_centre",
        "edit_general_paediatric_centre",
        "update_general_paediatric_centre_pressed",
        "paediatric_neurologist_referral_made",
        "paediatric_neurologist_referral_date",
        "paediatric_neurologist_input_date",
        "paediatric_neurology_centre",
        "edit_paediatric_neurology_centre",
        "update_paediatric_neurology_centre_pressed",
        "childrens_epilepsy_surgical_service_referral_criteria_met",
        "childrens_epilepsy_surgical_service_referral_made",
        "childrens_epilepsy_surgical_service_referral_date",
        "childrens_epilepsy_surgical_service_input_date",
        "epilepsy_surgery_centre",
        "edit_epilepsy_surgery_centre",
        "update_epilepsy_surgery_centre_pressed",
        "epilepsy_specialist_nurse_referral_made",
        "epilepsy_specialist_nurse_referral_date",
        "epilepsy_specialist_nurse_input_date",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in toggle_buttons:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all button clicks
                # 'general_paediatric_centre',                   button click                       assessment_id
                # 'edit_general_paediatric_centre',              button click                       assessment_id, site_id
                # 'update_general_paediatric_centre_pressed',    button click (edit/cancel)         assessment_id, site_id
                # 'paediatric_neurology_centre',                 button click                       assessment_id
                # 'edit_paediatric_neurology_centre',            button click                       assessment_id, site_id
                # 'update_paediatric_neurology_centre_pressed',  button click (edit/cancel)         assessment_id, site_id
                # 'epilepsy_surgery_centre',                     button click                       assessment_id
                # 'edit_epilepsy_surgery_centre',                button click                       assessment_id, site_id
                # 'update_epilepsy_surgery_centre_pressed',      button click (edit/cancel)         assessment_id, site_id
                if URL in [
                    "edit_general_paediatric_centre",
                    "update_general_paediatric_centre_pressed",
                    "edit_paediatric_neurology_centre",
                    "update_paediatric_neurology_centre_pressed",
                    "edit_epilepsy_surgery_centre",
                    "update_epilepsy_surgery_centre_pressed",
                ]:
                    # these all need assessment_id and site_id
                    current_site = E12SiteFactory(
                        case=CASE_FROM_DIFF_ORG,
                        organisation=DIFF_TRUST_DIFF_ORGANISATION,
                    )
                    if URL in [
                        "update_general_paediatric_centre_pressed",
                        "update_paediatric_neurology_centre_pressed",
                        "update_epilepsy_surgery_centre_pressed",
                    ]:
                        # these need accept a cancel or an edit param - testing the cancels here
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                    "action": "cancel",
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                        # assert cancel
                        assert (
                            response.status_code == HTTPStatus.FORBIDDEN
                        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment for {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"
                        # assert edit
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                    "action": "edit",
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                    else:
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                else:
                    response = client.post(
                        reverse(
                            URL,
                            kwargs={
                                "assessment_id": CASE_FROM_DIFF_ORG.registration.assessment.id,
                            },
                        ),
                        headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                        data={URL: 177},  # new organisation_id northampton general
                    )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment {URL} for {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_assessment_success(client):
    """
    Simulating different E12 Users attempting to update assessment in Epilepsy12

    Assert these users can change assessment
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields

    toggle_buttons = [
        "consultant_paediatrician_referral_made",
        "paediatric_neurologist_referral_made",
        "childrens_epilepsy_surgical_service_referral_criteria_met",
        "childrens_epilepsy_surgical_service_referral_made",
        "epilepsy_specialist_nurse_referral_made",
    ]

    date_fields = [
        "consultant_paediatrician_referral_date",
        "consultant_paediatrician_input_date",
        "paediatric_neurologist_referral_date",
        "paediatric_neurologist_input_date",
        "childrens_epilepsy_surgical_service_referral_date",
        "childrens_epilepsy_surgical_service_input_date",
        "epilepsy_specialist_nurse_referral_date",
        "epilepsy_specialist_nurse_input_date",
    ]

    URLS = [
        "consultant_paediatrician_referral_made",
        "consultant_paediatrician_referral_date",
        "consultant_paediatrician_input_date",
        "general_paediatric_centre",
        "edit_general_paediatric_centre",
        "update_general_paediatric_centre_pressed",
        "paediatric_neurologist_referral_made",
        "paediatric_neurologist_referral_date",
        "paediatric_neurologist_input_date",
        "paediatric_neurology_centre",
        "edit_paediatric_neurology_centre",
        "update_paediatric_neurology_centre_pressed",
        "childrens_epilepsy_surgical_service_referral_criteria_met",
        "childrens_epilepsy_surgical_service_referral_made",
        "childrens_epilepsy_surgical_service_referral_date",
        "childrens_epilepsy_surgical_service_input_date",
        "epilepsy_surgery_centre",
        "edit_epilepsy_surgery_centre",
        "update_epilepsy_surgery_centre_pressed",
        "epilepsy_specialist_nurse_referral_made",
        "epilepsy_specialist_nurse_referral_date",
        "epilepsy_specialist_nurse_input_date",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in toggle_buttons:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all button clicks
                # 'general_paediatric_centre',                   button click                       assessment_id
                # 'edit_general_paediatric_centre',              button click                       assessment_id, site_id
                # 'update_general_paediatric_centre_pressed',    button click (edit/cancel)         assessment_id, site_id
                # 'paediatric_neurology_centre',                 button click                       assessment_id
                # 'edit_paediatric_neurology_centre',            button click                       assessment_id, site_id
                # 'update_paediatric_neurology_centre_pressed',  button click (edit/cancel)         assessment_id, site_id
                # 'epilepsy_surgery_centre',                     button click                       assessment_id
                # 'edit_epilepsy_surgery_centre',                button click                       assessment_id, site_id
                # 'update_epilepsy_surgery_centre_pressed',      button click (edit/cancel)         assessment_id, site_id
                if URL in [
                    "edit_general_paediatric_centre",
                    "update_general_paediatric_centre_pressed",
                    "edit_paediatric_neurology_centre",
                    "update_paediatric_neurology_centre_pressed",
                    "edit_epilepsy_surgery_centre",
                    "update_epilepsy_surgery_centre_pressed",
                ]:
                    # these all need assessment_id and site_id
                    current_site = E12SiteFactory(
                        case=CASE_FROM_SAME_ORG,
                        organisation=TEST_USER_ORGANISATION,
                    )
                    if URL in [
                        "update_general_paediatric_centre_pressed",
                        "update_paediatric_neurology_centre_pressed",
                        "update_epilepsy_surgery_centre_pressed",
                    ]:
                        # these need accept a cancel or an edit param - testing the cancels here
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                    "action": "cancel",
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                        # assert cancel
                        assert (
                            response.status_code == HTTPStatus.OK
                        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"
                        # assert edit
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                    "action": "edit",
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                    else:
                        response = client.post(
                            reverse(
                                URL,
                                kwargs={
                                    "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                                    "site_id": current_site.pk,
                                },
                            ),
                            headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                            data={URL: 177},  # new organisation_id northampton general
                        )
                else:
                    response = client.post(
                        reverse(
                            URL,
                            kwargs={
                                "assessment_id": CASE_FROM_SAME_ORG.registration.assessment.id,
                            },
                        ),
                        headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                        data={URL: 177},  # new organisation_id northampton general
                    )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update Assessment {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_investigations_forbidden(client):
    """
    Simulating different E12 Users attempting to update investigations in Epilepsy12

    Assert these users cannot change investigations
    """

    # set up constants
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = [
        "eeg_request_date",
        "eeg_performed_date",
        "mri_brain_requested_date",
        "mri_brain_reported_date",
    ]

    toggle_buttons = [
        "eeg_indicated",
        "twelve_lead_ecg_status",
        "ct_head_scan_status",
        "mri_indicated",
    ]

    URLS = [
        "eeg_indicated",
        "eeg_request_date",
        "eeg_performed_date",
        "eeg_declined",
        "twelve_lead_ecg_status",
        "ct_head_scan_status",
        "mri_indicated",
        "mri_brain_requested_date",
        "mri_brain_reported_date",
        "mri_brain_declined",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in toggle_buttons:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_DIFF_ORG.registration.investigations.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_DIFF_ORG.registration.investigations.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all button clicks
                # these need accept an edit or a decline param - testing the confirm here
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_DIFF_ORG.registration.investigations.id,
                            "confirm": "edit",
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                )
                # assert edit
                assert (
                    response.status_code == HTTPStatus.FORBIDDEN
                ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment for {CASE_FROM_DIFF_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"
                # assert decline
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_DIFF_ORG.registration.investigations.id,
                            "confirm": "decline",
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment {URL} for {CASE_FROM_DIFF_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_investigations_success(client):
    """
    Simulating different E12 Users attempting to update investigations in Epilepsy12

    Assert these users can change investigations
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = [
        "eeg_request_date",
        "eeg_performed_date",
        "mri_brain_requested_date",
        "mri_brain_reported_date",
    ]

    toggle_buttons = [
        "eeg_indicated",
        "twelve_lead_ecg_status",
        "ct_head_scan_status",
        "mri_indicated",
    ]

    URLS = [
        "eeg_indicated",
        "eeg_request_date",
        "eeg_performed_date",
        "eeg_declined",
        "twelve_lead_ecg_status",
        "ct_head_scan_status",
        "mri_indicated",
        "mri_brain_requested_date",
        "mri_brain_reported_date",
        "mri_brain_declined",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in toggle_buttons:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_SAME_ORG.registration.investigations.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            elif URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_SAME_ORG.registration.investigations.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all button clicks
                # these need accept an edit or a decline param - testing the edit here
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_SAME_ORG.registration.investigations.id,
                            "confirm": "edit",
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                )
                # assert edit
                assert (
                    response.status_code == HTTPStatus.OK
                ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update assessment for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"
                # assert decline
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "investigations_id": CASE_FROM_SAME_ORG.registration.investigations.id,
                            "confirm": "decline",
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update Assessment {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_management_forbidden(client):
    """
    Simulating different E12 Users attempting to update management in Epilepsy12

    Assert these users cannot change management
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFFERENT_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = ["individualised_care_plan_date"]

    URLS = [
        "has_an_aed_been_given",
        "has_rescue_medication_been_prescribed",
        "individualised_care_plan_in_place",
        "individualised_care_plan_date",
        "individualised_care_plan_has_parent_carer_child_agreement",
        "individualised_care_plan_includes_service_contact_details",
        "individualised_care_plan_include_first_aid",
        "individualised_care_plan_parental_prolonged_seizure_care",
        "individualised_care_plan_includes_general_participation_risk",
        "individualised_care_plan_addresses_water_safety",
        "individualised_care_plan_addresses_sudep",
        "individualised_care_plan_includes_ehcp",
        "has_individualised_care_plan_been_updated_in_the_last_year",
        "has_been_referred_for_mental_health_support",
        "has_support_for_mental_health_support",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "management_id": CASE_FROM_DIFFERENT_ORG.registration.management.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all toggle buttons
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "management_id": CASE_FROM_DIFFERENT_ORG.registration.management.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update management {URL} for {CASE_FROM_DIFFERENT_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_management_success(client):
    """
    Simulating different E12 Users attempting to update management in Epilepsy12

    Assert these users can change management
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = ["individualised_care_plan_date"]

    URLS = [
        "has_an_aed_been_given",
        "has_rescue_medication_been_prescribed",
        "individualised_care_plan_in_place",
        "individualised_care_plan_date",
        "individualised_care_plan_has_parent_carer_child_agreement",
        "individualised_care_plan_includes_service_contact_details",
        "individualised_care_plan_include_first_aid",
        "individualised_care_plan_parental_prolonged_seizure_care",
        "individualised_care_plan_includes_general_participation_risk",
        "individualised_care_plan_addresses_water_safety",
        "individualised_care_plan_addresses_sudep",
        "individualised_care_plan_includes_ehcp",
        "has_individualised_care_plan_been_updated_in_the_last_year",
        "has_been_referred_for_mental_health_support",
        "has_support_for_mental_health_support",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            if URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "management_id": CASE_FROM_SAME_ORG.registration.management.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            else:
                # these are all toggle buttons
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "management_id": CASE_FROM_SAME_ORG.registration.management.id,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update Management {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_antiepilepsymedicine_forbidden(client):
    """
    Simulating different E12 Users attempting to update antiepilepsymedicine in Epilepsy12

    Assert these users cannot change antiepilepsymedicine
    """

    # set up constants

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        trust__ods_code="RGT",
    )

    CASE_FROM_DIFFERENT_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = [
        "antiepilepsy_medicine_start_date",
        "antiepilepsy_medicine_stop_date",
    ]

    toggle_buttons = [
        "antiepilepsy_medicine_risk_discussed",
        "is_a_pregnancy_prevention_programme_in_place",
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
    ]

    URLS = [
        "edit_antiepilepsy_medicine",
        "medicine_id",
        "antiepilepsy_medicine_start_date",
        "antiepilepsy_medicine_add_stop_date",
        "antiepilepsy_medicine_remove_stop_date",
        "antiepilepsy_medicine_stop_date",
        "antiepilepsy_medicine_risk_discussed",
        "is_a_pregnancy_prevention_programme_in_place",
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            antiepilepsy_medicine = E12AntiEpilepsyMedicineFactory(
                management=CASE_FROM_DIFFERENT_ORG.registration.management,
                is_rescue_medicine=True,
                medicine_entity=MedicineEntity.objects.get(pk=4),  # lorazepam
            )
            if URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "antiepilepsy_medicine_id": antiepilepsy_medicine.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            elif URL in toggle_buttons:
                # these are all toggle buttons
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "antiepilepsy_medicine_id": antiepilepsy_medicine.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            else:
                # these are all button clicks
                response = client.post(
                    reverse(
                        URL,
                        kwargs={"antiepilepsy_medicine_id": antiepilepsy_medicine.pk},
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested update antiepilepsymedicine {URL} for {CASE_FROM_DIFFERENT_ORG} in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_users_update_antiepilepsymedicine_success(client):
    """
    Simulating different E12 Users attempting to update antiepilepsymedicine in Epilepsy12

    Assert these users can change antiepilepsymedicine
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    user_first_names_for_test = [
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # fields
    date_fields = [
        "antiepilepsy_medicine_start_date",
        "antiepilepsy_medicine_stop_date",
    ]

    toggle_buttons = [
        "antiepilepsy_medicine_risk_discussed",
        "is_a_pregnancy_prevention_programme_in_place",
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
    ]

    URLS = [
        "edit_antiepilepsy_medicine",
        "medicine_id",
        "antiepilepsy_medicine_start_date",
        "antiepilepsy_medicine_add_stop_date",
        "antiepilepsy_medicine_remove_stop_date",
        "antiepilepsy_medicine_stop_date",
        "antiepilepsy_medicine_risk_discussed",
        "is_a_pregnancy_prevention_programme_in_place",
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
    ]

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        for URL in URLS:
            # carbamazepine
            antiepilepsy_medicine = E12AntiEpilepsyMedicineFactory(
                management=CASE_FROM_SAME_ORG.registration.management,
                is_rescue_medicine=True,
                medicine_entity=MedicineEntity.objects.get(
                    medicine_name="Carbamazepine"
                ),
            )

            if URL in date_fields:
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "antiepilepsy_medicine_id": antiepilepsy_medicine.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={URL: date.today()},
                )
            elif URL in toggle_buttons:
                # these are all toggle buttons
                response = client.post(
                    reverse(
                        URL,
                        kwargs={
                            "antiepilepsy_medicine_id": antiepilepsy_medicine.pk,
                        },
                    ),
                    headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
                )
            else:
                # these are all button clicks
                response = client.post(
                    reverse(
                        URL,
                        kwargs={"antiepilepsy_medicine_id": antiepilepsy_medicine.pk},
                    ),
                    headers={"Hx-Trigger-Name": URL, "Hx-Request": "true"},
                    data={"medicine_id": 8},  # Clobazam
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested to update AntiepilepsyMedicine {URL} for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected {HTTPStatus.OK} response status code, received {response.status_code}"
