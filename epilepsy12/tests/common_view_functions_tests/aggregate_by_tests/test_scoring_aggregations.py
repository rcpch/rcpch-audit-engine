"""Tests for aggregate_by.py functions.
"""

# python imports
import pytest
import random
from datetime import date

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_ethnicity,
    aggregate_all_eligible_kpi_fields,
    get_kpi_value_counts,
    all_registered_cases_for_cohort_and_abstraction_level,
    calculate_kpis,
    calculate_kpi_value_counts_queryset,
    update_kpi_aggregation_model,
    get_filtered_cases_queryset_for,
)
from epilepsy12.models import (
    Organisation,
    Case,
    Registration,
    OrganisationKPIAggregation,
    CountryKPIAggregation,
    ONSCountryEntity,
    OPENUKNetworkEntity,
    NHSRegionKPIAggregation,
    OpenUKKPIAggregation,
    ICBKPIAggregation,
    TrustKPIAggregation,
    NHSRegionEntity,
    IntegratedCareBoardEntity,
)
from epilepsy12.constants import (
    SEX_TYPE,
    DEPRIVATION_QUINTILES,
    ETHNICITIES,
    EnumAbstractionLevel,
)
from epilepsy12.tests.common_view_functions_tests.CreateKPIMetrics import KPIMetric



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
    """Tests the aggregate_all_eligible_kpi_fields fn returns scoring of KPIs. This is a larger, more complex test.

    For Cases with known KPI scorings, assert the output is correct.

    NOTE: using a different organisation to Cases already seeded in test db.

    METHOD:
        - define EXPECTED_KPI_SCORE_OUTPUT dict, all zeros initially

        - Over 50 iterations:
            1) Create a Case with attributes set according to KPI answers (automatically ineligible for KPIs 6,8,10)
            2) Create a Case with attributes set according to KPI answers (automatically ineligible for KPIs 3,5)

            NOTE:
                - The Case constructor gets these attributes from get_ans_dict_update_expected_score_dict fn. This fn also updates the EXPECTED_KPI_SCORE_OUTPUT eg. if it determines KPI_1 should 'PASS', it adds 1 to 'paediatrician_with_expertise_in_epilepsies' and 'paediatrician_with_expertise_in_epilepsies_total'
                - The Cases are all assigned to the same organisation

            3) calculate KPIs for each Case

        - assert aggregated_kpis == EXPECTED_KPI_SCORE_OUTPUT
    """

    # define constants
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

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

    # Generate KPIMetric objects
    kpi_metric_eligible_3_5_object = KPIMetric(
        eligible_kpi_3_5=True, eligible_kpi_6_8_10=False
    )
    kpi_metric_eligible_6_8_10_object = KPIMetric(
        eligible_kpi_3_5=False, eligible_kpi_6_8_10=True
    )

    def get_ans_dict_update_expected_score_dict(
        EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only
    ):
        """
        Generates a random answer dict for the E12CaseFactory constructor (according to KPIMetric's constraints), setting whichever attributes in related models required for each KPI to pass. Also returns an updated EXPECTED_KPI_SCORE_OUTPUT so this function avoids 'side-effects'.

        For nuances regarding eligibile_3_5_only, please see the KPIMetric docstrings.

        """

        # Dict to be returned
        ans_dict = {}

        for kpi_num in range(1, 11):
            if eligible_3_5_only:
                # The kpi_metric_eligible_3_5_object automatically sets these to ineligible
                if kpi_num in [6, 8, 10]:
                    continue
            else:
                # The kpi_metric_eligible_6_8_10_object automatically sets these to ineligible
                if kpi_num in [3, 5]:
                    continue

            OUTCOME_CHOICES = ["PASS", "FAIL"]

            # These KPIs can be ineligible from the E12CaseFactory constructor
            if kpi_num in [4, 7]:
                OUTCOME_CHOICES += ["INELIGIBLE"]

            outcome = random.choice(OUTCOME_CHOICES)

            kpi = f"kpi_{kpi_num}"
            kpi_names = KPI_MAP[
                kpi
            ]  # maps eg. kpi_1 -> paediatrician_with_expertise_in_epilepsies
            for kpi_name in kpi_names:
                # Update expected answer
                if outcome == "PASS":
                    EXPECTED_KPI_SCORE_OUTPUT[kpi_name] += 1
                    EXPECTED_KPI_SCORE_OUTPUT[f"{kpi_name}_total"] += 1
                elif outcome == "FAIL":
                    # Extra check for `parental_prolonged_seizures_care_plan` if kpi_9 = False => this sub-metric is set to INELIGIBLE in KPIMetric Class. Therefore, DON'T COUNT THIS in numerator nor denominator
                    if not kpi_name == "parental_prolonged_seizures_care_plan":
                        EXPECTED_KPI_SCORE_OUTPUT[f"{kpi_name}_total"] += 1

                # Updated kpi answers for E12CaseFactory constructor
                ans_dict.update({kpi: outcome})

        kpi_metric_object = (
            kpi_metric_eligible_3_5_object
            if eligible_3_5_only
            else kpi_metric_eligible_6_8_10_object
        )

        ans_dict_return = kpi_metric_object.generate_metrics(**ans_dict)

        return ans_dict_return, EXPECTED_KPI_SCORE_OUTPUT

    for _ in range(50):
        # Create and save child with these KPI answers (ELIGIBLE 3 + 5)
        (
            answers_3_5_eligible,
            EXPECTED_KPI_SCORE_OUTPUT,
        ) = get_ans_dict_update_expected_score_dict(
            EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only=True
        )

        CHILD = e12_case_factory(
            organisations__organisation=CHELWEST, **answers_3_5_eligible
        )
        EXPECTED_KPI_SCORE_OUTPUT["total_number_of_cases"] += 1

        registration = Registration.objects.get(case=CHILD)

        calculate_kpis(registration)

        # Create and save child with these KPI answers (ELIGIBLE 6 + 8 + 10)
        (
            answers_6_8_10_eligible,
            EXPECTED_KPI_SCORE_OUTPUT,
        ) = get_ans_dict_update_expected_score_dict(
            EXPECTED_KPI_SCORE_OUTPUT, eligible_3_5_only=False
        )

        CHILD = e12_case_factory(
            organisations__organisation=CHELWEST, **answers_6_8_10_eligible
        )
        EXPECTED_KPI_SCORE_OUTPUT["total_number_of_cases"] += 1

        registration = Registration.objects.get(case=CHILD)

        calculate_kpis(registration)

    # Add average keys
    only_numerators = [
        kpi
        for kpi in EXPECTED_KPI_SCORE_OUTPUT.keys()
        if not (kpi.endswith("_total") or kpi == "total_number_of_cases")
    ]

    for kpi in only_numerators:
        EXPECTED_KPI_SCORE_OUTPUT[f"{kpi}_average"] = (
            EXPECTED_KPI_SCORE_OUTPUT[kpi] / EXPECTED_KPI_SCORE_OUTPUT[f"{kpi}_total"]
        )

    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=CHELWEST,
        cohort=6,
        case_complete=False,
        abstraction_level="organisation",
    )

    aggregated_kpis = aggregate_all_eligible_kpi_fields(organisation_level)

    assert aggregated_kpis == EXPECTED_KPI_SCORE_OUTPUT


ALL_KPI_NAMES = [
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


@pytest.mark.django_db
def test_get_kpi_value_counts_eligible_3_5_pass_fail(e12_case_factory):
    """Test the get_kpi_value_counts fn returns correct aggregate. Tests:

    KPI 1 - 5, 7, 9
        PASS
        FAIL
        INCOMPLETE
    KPI 6, 8, 10
        INELIGIBLE
    """

    # test constants
    expected_output = {
        "paediatrician_with_expertise_in_epilepsies_passed": 10,
        "paediatrician_with_expertise_in_epilepsies_total_eligible": 20,
        "paediatrician_with_expertise_in_epilepsies_ineligible": 0,
        "paediatrician_with_expertise_in_epilepsies_incomplete": 10,
        "epilepsy_specialist_nurse_passed": 10,
        "epilepsy_specialist_nurse_total_eligible": 20,
        "epilepsy_specialist_nurse_ineligible": 0,
        "epilepsy_specialist_nurse_incomplete": 10,
        "tertiary_input_passed": 10,
        "tertiary_input_total_eligible": 20,
        "tertiary_input_ineligible": 0,
        "tertiary_input_incomplete": 10,
        "epilepsy_surgery_referral_passed": 10,
        "epilepsy_surgery_referral_total_eligible": 20,
        "epilepsy_surgery_referral_ineligible": 0,
        "epilepsy_surgery_referral_incomplete": 10,
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 0,
        "ecg_incomplete": 10,
        "mri_passed": 10,
        "mri_total_eligible": 20,
        "mri_ineligible": 0,
        "mri_incomplete": 10,
        "assessment_of_mental_health_issues_passed": 0,
        "assessment_of_mental_health_issues_total_eligible": 0,
        "assessment_of_mental_health_issues_ineligible": 30,
        "assessment_of_mental_health_issues_incomplete": 0,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 0,
        "mental_health_support_incomplete": 10,
        "sodium_valproate_passed": 0,
        "sodium_valproate_total_eligible": 0,
        "sodium_valproate_ineligible": 30,
        "sodium_valproate_incomplete": 0,
        "comprehensive_care_planning_agreement_passed": 10,
        "comprehensive_care_planning_agreement_total_eligible": 20,
        "comprehensive_care_planning_agreement_ineligible": 0,
        "comprehensive_care_planning_agreement_incomplete": 10,
        "patient_held_individualised_epilepsy_document_passed": 10,
        "patient_held_individualised_epilepsy_document_total_eligible": 20,
        "patient_held_individualised_epilepsy_document_ineligible": 0,
        "patient_held_individualised_epilepsy_document_incomplete": 10,
        "patient_carer_parent_agreement_to_the_care_planning_passed": 10,
        "patient_carer_parent_agreement_to_the_care_planning_total_eligible": 20,
        "patient_carer_parent_agreement_to_the_care_planning_ineligible": 0,
        "patient_carer_parent_agreement_to_the_care_planning_incomplete": 10,
        "care_planning_has_been_updated_when_necessary_passed": 10,
        "care_planning_has_been_updated_when_necessary_total_eligible": 20,
        "care_planning_has_been_updated_when_necessary_ineligible": 0,
        "care_planning_has_been_updated_when_necessary_incomplete": 10,
        "comprehensive_care_planning_content_passed": 10,
        "comprehensive_care_planning_content_total_eligible": 20,
        "comprehensive_care_planning_content_ineligible": 0,
        "comprehensive_care_planning_content_incomplete": 10,
        "parental_prolonged_seizures_care_plan_passed": 10,
        "parental_prolonged_seizures_care_plan_total_eligible": 10,
        "parental_prolonged_seizures_care_plan_ineligible": 10,
        "parental_prolonged_seizures_care_plan_incomplete": 10,
        "water_safety_passed": 10,
        "water_safety_total_eligible": 20,
        "water_safety_ineligible": 0,
        "water_safety_incomplete": 10,
        "first_aid_passed": 10,
        "first_aid_total_eligible": 20,
        "first_aid_ineligible": 0,
        "first_aid_incomplete": 10,
        "general_participation_and_risk_passed": 10,
        "general_participation_and_risk_total_eligible": 20,
        "general_participation_and_risk_ineligible": 0,
        "general_participation_and_risk_incomplete": 10,
        "service_contact_details_passed": 10,
        "service_contact_details_total_eligible": 20,
        "service_contact_details_ineligible": 0,
        "service_contact_details_incomplete": 10,
        "sudep_passed": 10,
        "sudep_total_eligible": 20,
        "sudep_ineligible": 0,
        "sudep_incomplete": 10,
        "school_individual_healthcare_plan_passed": 0,
        "school_individual_healthcare_plan_total_eligible": 0,
        "school_individual_healthcare_plan_ineligible": 30,
        "school_individual_healthcare_plan_incomplete": 0,
    }
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

    # create answersets for cases to achieve the stated expected output
    answer_object = KPIMetric(eligible_kpi_3_5=True)
    pass_answers = answer_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_3="PASS",
        kpi_4="PASS",
        kpi_5="PASS",
        kpi_7="PASS",
        kpi_9="PASS",
    )
    fail_answers = answer_object.generate_metrics(
        kpi_1="FAIL",
        kpi_2="FAIL",
        kpi_3="FAIL",
        kpi_4="FAIL",
        kpi_5="FAIL",
        kpi_7="FAIL",
        kpi_9="FAIL",
    )

    filled_case_objects = []

    # iterate through answersets (pass, fail, none) for kpi, create Cases
    for answer_set in [
        pass_answers,
        fail_answers,
        {},
    ]:
        test_cases = e12_case_factory.create_batch(
            10, organisations__organisation=CHELWEST, first_name="tester", **answer_set
        )
        filled_case_objects += test_cases

    for test_case in filled_case_objects:
        calculate_kpis(registration_instance=test_case.registration)

    # Get just these test cases
    filtered_cases = Case.objects.filter(first_name="tester")

    result = get_kpi_value_counts(
        filtered_cases=filtered_cases,
        kpi_measures=ALL_KPI_NAMES,
    )

    assert result == expected_output


@pytest.mark.django_db
def test_get_kpi_value_counts_eligible_6_8_10_pass_fail(e12_case_factory):
    """Test the refactored `get_kpi_value_counts` fn returns correct aggregate.

    Tests:
    KPI 1,2,3,4,6,7,8,9,10
        PASS
        FAIL
        INCOMPLETE
    KPI 3,5
        INCOMPLETE
        INELIGIBLE

    """
    # define test constants
    expected_output = {
        "paediatrician_with_expertise_in_epilepsies_passed": 10,
        "paediatrician_with_expertise_in_epilepsies_total_eligible": 20,
        "paediatrician_with_expertise_in_epilepsies_ineligible": 0,
        "paediatrician_with_expertise_in_epilepsies_incomplete": 10,
        "epilepsy_specialist_nurse_passed": 10,
        "epilepsy_specialist_nurse_total_eligible": 20,
        "epilepsy_specialist_nurse_ineligible": 0,
        "epilepsy_specialist_nurse_incomplete": 10,
        "tertiary_input_passed": 0,
        "tertiary_input_total_eligible": 0,
        "tertiary_input_ineligible": 30,
        "tertiary_input_incomplete": 0,
        "epilepsy_surgery_referral_passed": 0,
        "epilepsy_surgery_referral_total_eligible": 0,
        "epilepsy_surgery_referral_ineligible": 20,
        "epilepsy_surgery_referral_incomplete": 10,
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 0,
        "ecg_incomplete": 10,
        "mri_passed": 0,
        "mri_total_eligible": 0,
        "mri_ineligible": 20,
        "mri_incomplete": 10,
        "assessment_of_mental_health_issues_passed": 10,
        "assessment_of_mental_health_issues_total_eligible": 20,
        "assessment_of_mental_health_issues_ineligible": 0,
        "assessment_of_mental_health_issues_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 0,
        "mental_health_support_incomplete": 10,
        "sodium_valproate_passed": 10,
        "sodium_valproate_total_eligible": 20,
        "sodium_valproate_ineligible": 10,
        "sodium_valproate_incomplete": 0,
        "comprehensive_care_planning_agreement_passed": 10,
        "comprehensive_care_planning_agreement_total_eligible": 20,
        "comprehensive_care_planning_agreement_ineligible": 0,
        "comprehensive_care_planning_agreement_incomplete": 10,
        "patient_held_individualised_epilepsy_document_passed": 10,
        "patient_held_individualised_epilepsy_document_total_eligible": 20,
        "patient_held_individualised_epilepsy_document_ineligible": 0,
        "patient_held_individualised_epilepsy_document_incomplete": 10,
        "patient_carer_parent_agreement_to_the_care_planning_passed": 10,
        "patient_carer_parent_agreement_to_the_care_planning_total_eligible": 20,
        "patient_carer_parent_agreement_to_the_care_planning_ineligible": 0,
        "patient_carer_parent_agreement_to_the_care_planning_incomplete": 10,
        "care_planning_has_been_updated_when_necessary_passed": 10,
        "care_planning_has_been_updated_when_necessary_total_eligible": 20,
        "care_planning_has_been_updated_when_necessary_ineligible": 0,
        "care_planning_has_been_updated_when_necessary_incomplete": 10,
        "comprehensive_care_planning_content_passed": 10,
        "comprehensive_care_planning_content_total_eligible": 20,
        "comprehensive_care_planning_content_ineligible": 0,
        "comprehensive_care_planning_content_incomplete": 10,
        "parental_prolonged_seizures_care_plan_passed": 10,
        "parental_prolonged_seizures_care_plan_total_eligible": 10,
        "parental_prolonged_seizures_care_plan_ineligible": 10,
        "parental_prolonged_seizures_care_plan_incomplete": 10,
        "water_safety_passed": 10,
        "water_safety_total_eligible": 20,
        "water_safety_ineligible": 0,
        "water_safety_incomplete": 10,
        "first_aid_passed": 10,
        "first_aid_total_eligible": 20,
        "first_aid_ineligible": 0,
        "first_aid_incomplete": 10,
        "general_participation_and_risk_passed": 10,
        "general_participation_and_risk_total_eligible": 20,
        "general_participation_and_risk_ineligible": 0,
        "general_participation_and_risk_incomplete": 10,
        "service_contact_details_passed": 10,
        "service_contact_details_total_eligible": 20,
        "service_contact_details_ineligible": 0,
        "service_contact_details_incomplete": 10,
        "sudep_passed": 10,
        "sudep_total_eligible": 20,
        "sudep_ineligible": 0,
        "sudep_incomplete": 10,
        "school_individual_healthcare_plan_passed": 10,
        "school_individual_healthcare_plan_total_eligible": 20,
        "school_individual_healthcare_plan_ineligible": 0,
        "school_individual_healthcare_plan_incomplete": 10,
    }
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

    # create answersets for cases to achieve the stated expected output
    answer_object = KPIMetric(eligible_kpi_6_8_10=True)
    pass_answers = answer_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_4="PASS",
        kpi_6="PASS",
        kpi_7="PASS",
        kpi_8="PASS",
        kpi_9="PASS",
        kpi_10="PASS",
    )
    fail_answers = answer_object.generate_metrics(
        kpi_1="FAIL",
        kpi_2="FAIL",
        kpi_4="FAIL",
        kpi_6="FAIL",
        kpi_7="FAIL",
        kpi_8="FAIL",
        kpi_9="FAIL",
        kpi_10="FAIL",
    )

    filled_case_objects = []
    # iterate through answersets (pass, fail, none) for kpi, create Cases
    # NOTE: here we specify date of birth for 'empty answer set', as the default age would otherwise be 1yo, making them ineligible for kpis 6,8,10
    for answer_set in [pass_answers, fail_answers, {"date_of_birth": date(2011, 1, 1)}]:
        test_cases = e12_case_factory.create_batch(
            10, organisations__organisation=CHELWEST, first_name="tester", **answer_set
        )
        filled_case_objects += test_cases

    for test_case in filled_case_objects:
        calculate_kpis(registration_instance=test_case.registration)

    # Get just these test cases
    filtered_cases = Case.objects.filter(first_name="tester")

    result = get_kpi_value_counts(
        filtered_cases=filtered_cases,
        kpi_measures=ALL_KPI_NAMES,
    )

    assert result == expected_output


@pytest.mark.django_db
def test_get_kpi_value_counts_others_ineligible(e12_case_factory):
    """Test the refactored `get_kpi_value_counts` fn returns correct aggregate.

    Due to the construction of the `KPIMetrics` class, the remaining possibility of kpi measure scores includes ineligible for kpi 4 + 7. This is a separate test to the previous two for clarity.

    Tests:

    KPI 4,7 (also 3,5 -> previously tested)
        INELIGIBLE
    KPI 1,2,6,8,9,10
        PASS


    """
    expected_output = {
        "paediatrician_with_expertise_in_epilepsies_passed": 10,
        "paediatrician_with_expertise_in_epilepsies_total_eligible": 10,
        "paediatrician_with_expertise_in_epilepsies_ineligible": 0,
        "paediatrician_with_expertise_in_epilepsies_incomplete": 0,
        "epilepsy_specialist_nurse_passed": 10,
        "epilepsy_specialist_nurse_total_eligible": 10,
        "epilepsy_specialist_nurse_ineligible": 0,
        "epilepsy_specialist_nurse_incomplete": 0,
        "tertiary_input_passed": 0,
        "tertiary_input_total_eligible": 0,
        "tertiary_input_ineligible": 10,
        "tertiary_input_incomplete": 0,
        "epilepsy_surgery_referral_passed": 0,
        "epilepsy_surgery_referral_total_eligible": 0,
        "epilepsy_surgery_referral_ineligible": 10,
        "epilepsy_surgery_referral_incomplete": 0,
        "ecg_passed": 0,
        "ecg_total_eligible": 0,
        "ecg_ineligible": 10,
        "ecg_incomplete": 0,
        "mri_passed": 0,
        "mri_total_eligible": 0,
        "mri_ineligible": 10,
        "mri_incomplete": 0,
        "assessment_of_mental_health_issues_passed": 10,
        "assessment_of_mental_health_issues_total_eligible": 10,
        "assessment_of_mental_health_issues_ineligible": 0,
        "assessment_of_mental_health_issues_incomplete": 0,
        "mental_health_support_passed": 0,
        "mental_health_support_total_eligible": 0,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 0,
        "sodium_valproate_passed": 10,
        "sodium_valproate_total_eligible": 10,
        "sodium_valproate_ineligible": 0,
        "sodium_valproate_incomplete": 0,
        "comprehensive_care_planning_agreement_passed": 10,
        "comprehensive_care_planning_agreement_total_eligible": 10,
        "comprehensive_care_planning_agreement_ineligible": 0,
        "comprehensive_care_planning_agreement_incomplete": 0,
        "patient_held_individualised_epilepsy_document_passed": 10,
        "patient_held_individualised_epilepsy_document_total_eligible": 10,
        "patient_held_individualised_epilepsy_document_ineligible": 0,
        "patient_held_individualised_epilepsy_document_incomplete": 0,
        "patient_carer_parent_agreement_to_the_care_planning_passed": 10,
        "patient_carer_parent_agreement_to_the_care_planning_total_eligible": 10,
        "patient_carer_parent_agreement_to_the_care_planning_ineligible": 0,
        "patient_carer_parent_agreement_to_the_care_planning_incomplete": 0,
        "care_planning_has_been_updated_when_necessary_passed": 10,
        "care_planning_has_been_updated_when_necessary_total_eligible": 10,
        "care_planning_has_been_updated_when_necessary_ineligible": 0,
        "care_planning_has_been_updated_when_necessary_incomplete": 0,
        "comprehensive_care_planning_content_passed": 10,
        "comprehensive_care_planning_content_total_eligible": 10,
        "comprehensive_care_planning_content_ineligible": 0,
        "comprehensive_care_planning_content_incomplete": 0,
        "parental_prolonged_seizures_care_plan_passed": 10,
        "parental_prolonged_seizures_care_plan_total_eligible": 10,
        "parental_prolonged_seizures_care_plan_ineligible": 0,
        "parental_prolonged_seizures_care_plan_incomplete": 0,
        "water_safety_passed": 10,
        "water_safety_total_eligible": 10,
        "water_safety_ineligible": 0,
        "water_safety_incomplete": 0,
        "first_aid_passed": 10,
        "first_aid_total_eligible": 10,
        "first_aid_ineligible": 0,
        "first_aid_incomplete": 0,
        "general_participation_and_risk_passed": 10,
        "general_participation_and_risk_total_eligible": 10,
        "general_participation_and_risk_ineligible": 0,
        "general_participation_and_risk_incomplete": 0,
        "service_contact_details_passed": 10,
        "service_contact_details_total_eligible": 10,
        "service_contact_details_ineligible": 0,
        "service_contact_details_incomplete": 0,
        "sudep_passed": 10,
        "sudep_total_eligible": 10,
        "sudep_ineligible": 0,
        "sudep_incomplete": 0,
        "school_individual_healthcare_plan_passed": 10,
        "school_individual_healthcare_plan_total_eligible": 10,
        "school_individual_healthcare_plan_ineligible": 0,
        "school_individual_healthcare_plan_incomplete": 0,
    }
    CHELWEST = Organisation.objects.get(
        ODSCode="RQM01",
        ParentOrganisation_ODSCode="RQM",
    )

    # create answersets for cases to achieve the stated expected output
    answer_object = KPIMetric(eligible_kpi_6_8_10=True)
    ineligible_or_pass_answers = answer_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_4="INELIGIBLE",
        kpi_6="PASS",
        kpi_7="INELIGIBLE",
        kpi_8="PASS",
        kpi_9="PASS",
        kpi_10="PASS",
    )

    filled_case_objects = []
    # iterate through answersets (pass, fail, none) for kpi, create Cases
    test_cases = e12_case_factory.create_batch(
        10,
        organisations__organisation=CHELWEST,
        first_name="tester",
        **ineligible_or_pass_answers,
    )
    filled_case_objects += test_cases

    for test_case in filled_case_objects:
        calculate_kpis(registration_instance=test_case.registration)

    # Get just these test cases
    filtered_cases = Case.objects.filter(first_name="tester")

    result = get_kpi_value_counts(
        filtered_cases=filtered_cases,
        kpi_measures=ALL_KPI_NAMES,
    )

    assert result == expected_output


@pytest.mark.django_db
def test_debug(e12_case_factory):
    """debug"""
    pass