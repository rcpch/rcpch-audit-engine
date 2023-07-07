"""Tests for aggregate_by.py functions.
"""

# python imports
import pytest
import random

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_ethnicity,
    aggregate_all_eligible_kpi_fields,
    all_registered_cases_for_cohort_and_abstraction_level,
    calculate_kpis,
)
from epilepsy12.models import (
    Organisation,
    Case,
    KPI,
    Registration,
)
from epilepsy12.constants import (
    SEX_TYPE,
    DEPRIVATION_QUINTILES,
    ETHNICITIES,
    KPI_SCORE,
)
from epilepsy12.tests.common_view_functions_tests.CreateKPIMetrics import KPIMetric


@pytest.mark.django_db
def test_cases_aggregated_by_sex(e12_case_factory):
    """Tests the cases_aggregated_by_sex fn returns correct count.

    NOTE: There is already 1 seeded Case in the test db. In this test setup, we seed 10 children per SEX_TYPE (n=4).

    Thus expected total count is 10 for each sex, except Male, which is 11.
    """

    # define constants
    GOSH = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    # Create 10 cases of each available sex type
    for sex_type in SEX_TYPE:
        # For each sex, assign 10 cases
        e12_case_factory.create_batch(
            size=10,
            sex=sex_type[0],
            registration=None,  # ensure related audit factories not generated
            organisations__organisation=GOSH,
        )

    cases_queryset = cases_aggregated_by_sex(selected_organisation=GOSH)

    expected_counts = {
        "Female": 10,
        "Not Known": 10,
        "Not Specified": 10,
        "Male": 11,
    }

    for aggregate in cases_queryset:
        SEX = aggregate["sex_display"]

        assert (
            aggregate["sexes"] == expected_counts[SEX]
        ), f"`cases_aggregated_by_sex` output does not match expected output for {SEX}. Output {aggregate['sexes']} but expected {expected_counts[SEX]}."


@pytest.mark.django_db
def test_cases_aggregated_by_deprivation_score(e12_case_factory, e12_site_factory):
    """Tests the cases_aggregated_by_deprivation_score fn returns correct count."""

    # define constants
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

    # Loop through each deprivation quintile
    for deprivation_type in DEPRIVATION_QUINTILES.deprivation_quintiles:
        # For each deprivation, assign 10 cases, add to cases_list
        e12_case_factory.create_batch(
            size=10,
            index_of_multiple_deprivation_quintile=deprivation_type,
            registration=None,  # ensure related audit factories not generated
            organisations__organisation=CHELWEST,
        )

    expected_counts = [
        {
            "index_of_multiple_deprivation_quintile_display": 1,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "1st quintile",
        },
        {
            "index_of_multiple_deprivation_quintile_display": 2,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "2nd quintile",
        },
        {
            "index_of_multiple_deprivation_quintile_display": 3,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "3rd quintile",
        },
        {
            "index_of_multiple_deprivation_quintile_display": 4,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "4th quintile",
        },
        {
            "index_of_multiple_deprivation_quintile_display": 5,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "5th quintile",
        },
        {
            "index_of_multiple_deprivation_quintile_display": 6,
            "cases_aggregated_by_deprivation": 10,
            "index_of_multiple_deprivation_quintile_display_str": "Not known",
        },
    ]

    cases_queryset = cases_aggregated_by_deprivation_score(CHELWEST)

    for ix, aggregate in enumerate(cases_queryset):
        assert (
            aggregate == expected_counts[ix]
        ), f"Expected aggregate count for cases_aggregated_by_deprivation_score not matching output."


@pytest.mark.django_db
def test_cases_aggregated_by_ethnicity(e12_case_factory):
    """Tests the cases_aggregated_by_ethnicity fn returns correct count."""

    # define constants
    GOSH = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    # Loop through each ethnicity
    for ethnicity_type in ETHNICITIES:
        # For each deprivation, assign 10 cases, add to cases_list
        e12_case_factory.create_batch(
            size=10,
            ethnicity=ethnicity_type[0],
            registration=None,  # ensure related audit factories not generated
            organisations__organisation=GOSH,
        )

    cases_queryset = cases_aggregated_by_ethnicity(selected_organisation=GOSH)

    expected_counts = [
        {"ethnicity_display": "Pakistani or British Pakistani", "ethnicities": 10},
        {"ethnicity_display": "Any other Asian background", "ethnicities": 10},
        {"ethnicity_display": "Any other Black background", "ethnicities": 10},
        {"ethnicity_display": "Any other ethnic group", "ethnicities": 10},
        {"ethnicity_display": "Any other mixed background", "ethnicities": 10},
        {"ethnicity_display": "Any other White background", "ethnicities": 10},
        {"ethnicity_display": "Bangladeshi or British Bangladeshi", "ethnicities": 10},
        {"ethnicity_display": "African", "ethnicities": 10},
        {"ethnicity_display": "Caribbean", "ethnicities": 10},
        {"ethnicity_display": "Chinese", "ethnicities": 10},
        {"ethnicity_display": "Indian or British Indian", "ethnicities": 10},
        {"ethnicity_display": "Irish", "ethnicities": 10},
        {"ethnicity_display": "Mixed (White and Asian)", "ethnicities": 10},
        {"ethnicity_display": "Mixed (White and Black African)", "ethnicities": 10},
        {"ethnicity_display": "Mixed (White and Black Caribbean)", "ethnicities": 10},
        {"ethnicity_display": "Not Stated", "ethnicities": 10},
        {
            "ethnicity_display": "British, Mixed British",
            "ethnicities": 11,
        },  # 11 AS THERE IS ALREADY A SEEDED CASE IN TEST DB
    ]

    for ix, aggregate in enumerate(cases_queryset):
        assert (
            aggregate == expected_counts[ix]
        ), f"Expected aggregate count for cases_aggregated_by_ethnicity not matching output: {aggregate} should be {expected_counts[ix]}"


@pytest.mark.django_db
def test_aggregate_all_eligible_kpi_fields_correct_fields_present(e12_case_factory):
    """Tests the aggregate_all_eligible_kpi_fields fn returns all the KPI fields."""

    # define constants
    GOSH = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    COHORT = 6

    # create a KPI object
    kpi_metric_eligible_3_5_object = KPIMetric(
        eligible_kpi_3_5=True, eligible_kpi_6_8_10=False
    )

    # generate answer set dict for e12_case_factory constructor
    answers_eligible_3_5 = kpi_metric_eligible_3_5_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_3="PASS",
        kpi_4="PASS",
        kpi_5="PASS",
        kpi_7="PASS",
        kpi_9="PASS",
    )

    e12_case_factory.create_batch(
        size=10,
        organisations__organisation=GOSH,
        **answers_eligible_3_5,
    )

    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=GOSH,
        cohort=COHORT,
        case_complete=False,
        abstraction_level="organisation",
    )

    aggregated_kpis = aggregate_all_eligible_kpi_fields(organisation_level)

    all_kpi_measures = [
        "paediatrician_with_expertise_in_epilepsies",
        "epilepsy_specialist_nurse",
        "tertiary_input",
        "epilepsy_surgery_referral",
        "ecg",
        "mri",
        "assessment_of_mental_health_issues",
        "mental_health_support",
        "sodium_valproate",
        "comprehensive_care_planning_agreement",
        "patient_held_individualised_epilepsy_document",
        "patient_carer_parent_agreement_to_the_care_planning",
        "care_planning_has_been_updated_when_necessary",
        "comprehensive_care_planning_content",
        "parental_prolonged_seizures_care_plan",
        "water_safety",
        "first_aid",
        "general_participation_and_risk",
        "service_contact_details",
        "sudep",
        "school_individual_healthcare_plan",
    ]

    for kpi in all_kpi_measures:
        assert (
            kpi in aggregated_kpis
        ), f"{kpi} not present in aggregate_all_eligible_kpi_fields output."

        assert (
            f"{kpi}_average"
        ), f"{kpi}_average not present in aggregate_all_eligible_kpi_fields output."

        assert (
            f"{kpi}_total"
        ), f"{kpi}_total not present in aggregate_all_eligible_kpi_fields output."


@pytest.mark.django_db
def test_aggregate_all_eligible_kpi_fields_correct_kpi_scoring(e12_case_factory):
    """Tests the aggregate_all_eligible_kpi_fields fn returns scoring of KPIs.

    For Cases with known KPI scorings, assert the output is correct.

    NOTE: using a different organisation to Cases already seeded in db.

    METHOD:

        - define EXPECTED_KPI_SCORE_OUTPUT dict
        - Get 1 KPIMetric Object each for eligible_kpi_3_5=True, eligible_kpi_6_8_10=True
        - .generate_metrics(), for each kpi:
                random_choice(['PASS','FAIL','INELIGIBLE']) *THIS IS DIFF FOR EACH KPI*
                if ('PASS'):
                    EXPECTED_KPI_SCORE_OUTPUT[kpi]+=1
                    EXPECTED_KPI_SCORE_OUTPUT[kpi_total]+=1
                elif ('FAIL'):
                    EXPECTED_KPI_SCORE_OUTPUT[kpi]+=0
                    EXPECTED_KPI_SCORE_OUTPUT[kpi_total]+=1
                else:
                    pass

        - feed into 10 E12CaseFactory's
        - compare output with expected
    """

    # define constants
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

    KPI_NAMES = [
        "paediatrician_with_expertise_in_epilepsies",
        "epilepsy_specialist_nurse",
        "tertiary_input",
        "epilepsy_surgery_referral",
        "ecg",
        "mri",
        "assessment_of_mental_health_issues",
        "mental_health_support",
        "sodium_valproate",
        "comprehensive_care_planning_agreement",
        "patient_held_individualised_epilepsy_document",
        "patient_carer_parent_agreement_to_the_care_planning",
        "care_planning_has_been_updated_when_necessary",
        "comprehensive_care_planning_content",
        "parental_prolonged_seizures_care_plan",
        "water_safety",
        "first_aid",
        "general_participation_and_risk",
        "service_contact_details",
        "sudep",
        "school_individual_healthcare_plan",
    ]

    KPI_MAP = {
        "kpi_1": ["paediatrician_with_expertise_in_epilepsies"],
        "kpi_2": ["epilepsy_specialist_nurse"],
        "kpi_3": ["tertiary_input", "epilepsy_surgery_referral"],
        "kpi_4": ["ecg"],
        "kpi_5": ["mri"],
        "kpi_6": ["assessment_of_mental_health_issues"],
        "kpi_7": ["mental_health_support"],
        "kpi_8": ["sodium_valproate"],
        "kpi_9": [
            "comprehensive_care_planning_agreement",
            "patient_held_individualised_epilepsy_document",
            "patient_carer_parent_agreement_to_the_care_planning",
            "care_planning_has_been_updated_when_necessary",
            "comprehensive_care_planning_content",
            "parental_prolonged_seizures_care_plan",
            "water_safety",
            "first_aid",
            "general_participation_and_risk",
            "service_contact_details",
            "sudep",
        ],
        "kpi_10": ["school_individual_healthcare_plan"],
    }

    EXPECTED_KPI_SCORE_OUTPUT = {
        "paediatrician_with_expertise_in_epilepsies": 0,
        "paediatrician_with_expertise_in_epilepsies_total": 0,
        "epilepsy_specialist_nurse": 0,
        "epilepsy_specialist_nurse_total": 0,
        "tertiary_input": 0,
        "tertiary_input_total": 0,
        "epilepsy_surgery_referral": 0,
        "epilepsy_surgery_referral_total": 0,
        "ecg": 0,
        "ecg_total": 0,
        "mri": 0,
        "mri_total": 0,
        "assessment_of_mental_health_issues": 0,
        "assessment_of_mental_health_issues_total": 0,
        "mental_health_support": 0,
        "mental_health_support_total": 0,
        "sodium_valproate": 0,
        "sodium_valproate_total": 0,
        "comprehensive_care_planning_agreement": 0,
        "comprehensive_care_planning_agreement_total": 0,
        "patient_held_individualised_epilepsy_document": 0,
        "patient_held_individualised_epilepsy_document_total": 0,
        "patient_carer_parent_agreement_to_the_care_planning": 0,
        "patient_carer_parent_agreement_to_the_care_planning_total": 0,
        "care_planning_has_been_updated_when_necessary": 0,
        "care_planning_has_been_updated_when_necessary_total": 0,
        "comprehensive_care_planning_content": 0,
        "comprehensive_care_planning_content_total": 0,
        "parental_prolonged_seizures_care_plan": 0,
        "parental_prolonged_seizures_care_plan_total": 0,
        "water_safety": 0,
        "water_safety_total": 0,
        "first_aid": 0,
        "first_aid_total": 0,
        "general_participation_and_risk": 0,
        "general_participation_and_risk_total": 0,
        "service_contact_details": 0,
        "service_contact_details_total": 0,
        "sudep": 0,
        "sudep_total": 0,
        "school_individual_healthcare_plan": 0,
        "school_individual_healthcare_plan_total": 0,
        "total_number_of_cases": 0,
    }

    kpi_metric_eligible_3_5_object = KPIMetric(
        eligible_kpi_3_5=True, eligible_kpi_6_8_10=False
    )
    kpi_metric_eligible_6_8_10_object = KPIMetric(
        eligible_kpi_3_5=False, eligible_kpi_6_8_10=True
    )
    
    # Temp varaiable for debugging - shows answers insert into case constructors
    assigned_outcomes = {}

    # generate kpi_metric_eligible_3_5_object answer set for e12_case_factory constructor
    def get_ans_dict_update_expected_score_dict(EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only):
        ans_dict = {}
        for kpi_num in range(1, 11):
            
            if eligible_3_5_only:
                # The kpi_metric_eligible_3_5_object automatically sets these to ineligible
                if kpi_num in [6, 8, 10]:
                    continue
            else:
                # The kpi_metric_eligible_6_8_10_object automatically sets these to ineligible
                if kpi_num in [3,5]:
                    continue
            
            OUTCOME_CHOICES = ['PASS','FAIL']
            
            
            if kpi_num in [4, 7]:
                OUTCOME_CHOICES += ["INELIGIBLE"]

            outcome = random.choice(OUTCOME_CHOICES)
            
            kpi = f"kpi_{kpi_num}"
            kpi_names = KPI_MAP[kpi]
            
            
            for kpi_name in kpi_names:
                
                # Update expected answer
                if outcome == "PASS":
                    EXPECTED_KPI_SCORE_OUTPUT[kpi_name] += 1
                    EXPECTED_KPI_SCORE_OUTPUT[f"{kpi_name}_total"] += 1
                elif outcome == "FAIL":
                    EXPECTED_KPI_SCORE_OUTPUT[f"{kpi_name}_total"] += 1

                # Updated kpi answers for E12CaseFactory constructor
                ans_dict.update({kpi:outcome})
                
                # TEMP VAR FOR DEBUGGING _ SHOWS ANSWERS ASSIGNED
                temp_name = f"{kpi}-{kpi_name}"
                
                if assigned_outcomes.get(temp_name):
                    assigned_outcomes[temp_name] += [outcome]
                else:
                    assigned_outcomes[temp_name] = [outcome]
                    
        
        kpi_metric_object = kpi_metric_eligible_3_5_object if eligible_3_5_only else kpi_metric_eligible_6_8_10_object        
        
        ans_dict_return = kpi_metric_object.generate_metrics(
            **ans_dict
            )
        
        return ans_dict_return, EXPECTED_KPI_SCORE_OUTPUT

    
    
    for _ in range(10):
        
        # Create and save child with these KPI answers (ELIGIBLE 3 + 5)
        answers_3_5_eligible, EXPECTED_KPI_SCORE_OUTPUT = get_ans_dict_update_expected_score_dict(EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only=True)
        
        CHILD = e12_case_factory(
            organisations__organisation=CHELWEST,
            **answers_3_5_eligible
        )
        EXPECTED_KPI_SCORE_OUTPUT['total_number_of_cases'] += 1

        registration = Registration.objects.get(case=CHILD)

        calculate_kpis(registration)
        
        # Create and save child with these KPI answers (ELIGIBLE 6 + 8 + 10)
        answers_6_8_10_eligible, EXPECTED_KPI_SCORE_OUTPUT = get_ans_dict_update_expected_score_dict(EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only=False)
        
        CHILD = e12_case_factory(
            organisations__organisation=CHELWEST,
            **answers_6_8_10_eligible
        )
        EXPECTED_KPI_SCORE_OUTPUT['total_number_of_cases'] += 1

        registration = Registration.objects.get(case=CHILD)

        calculate_kpis(registration)
        
        

    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=CHELWEST,
        cohort=6,
        case_complete=False,
        abstraction_level="organisation",
    )

    aggregated_kpis = aggregate_all_eligible_kpi_fields(organisation_level)
    
    
    # REMOVE AVERAGE COUNTS FROM DICT FOR NOW
    aggregated_kpis = {key: value for key, value in aggregated_kpis.items() if not key.endswith("_average")}
    
    # [print(agg, val) for agg,val in aggregated_kpis.items()]

    [print(f"{kpi}:{outcome}") for kpi,outcome in assigned_outcomes.items()]
    
    assert aggregated_kpis == EXPECTED_KPI_SCORE_OUTPUT
