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


def _register_kpi_scored_cases(e12_case_factory, ods_codes: "list[str]"):
    """Helper function to return a queryset of 60 kids with scored, known KPI scores."""
    ORGANISATIONS = Organisation.objects.filter(
        ODSCode__in=ods_codes,
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
    ineligible_answers = answer_object.generate_metrics(
        kpi_1="FAIL",
        kpi_2="FAIL",
        kpi_4="INELIGIBLE",
        kpi_6="FAIL",
        kpi_7="INELIGIBLE",
        kpi_8="FAIL",
        kpi_9="FAIL",
        kpi_10="FAIL",
    )
    # NOTE: here we specify date of birth for 'empty answer set', as the default age would otherwise be 1yo, making them ineligible for kpis 6,8,10
    incomplete_answers = {"date_of_birth": date(2011, 1, 1)}

    filled_case_objects = []
    # iterate through answersets (pass, fail, ineligble, incomplete) for kpi, create 10 Cases per answerset
    for organisation in ORGANISATIONS:
        for answer_set in [
            pass_answers,
            fail_answers,
            ineligible_answers,
            incomplete_answers,
        ]:
            test_cases = e12_case_factory.create_batch(
                10,
                organisations__organisation=organisation,
                first_name=f"temp_{organisation.OrganisationName}",
                **answer_set,
            )
            filled_case_objects += test_cases

    for test_case in filled_case_objects:
        calculate_kpis(registration_instance=test_case.registration)


def _clean_cases_from_test_db() -> None:
    Registration.objects.all().delete()
    Case.objects.all().delete()


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_organisation_level(e12_case_factory):
    """This test generates 60 children total at 2 different organisations (30 each), with known KPI scorings. Asserts the value counts function returns the expected KPI value counts.

    NOTE: To simplify the expected score fields, we just use 2 KPIs. This is a valid simplification as the function does not touch KPI scorings - only getting scorings from the model and aggregating. Thus, if it works for 2 kpis (or even 1), it should work for all.
    NOTE: the 2 different organisations (Addenbrooke's Hospital and YSBYTY YSTRAD FAWR [chosen as first and last alphabetically]) are chosen as they differ at each level of abstraction.
    """

    # Clean
    _clean_cases_from_test_db()

    ods_codes = ["RGT01", "RQM01"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {ods_code: kpi_scores_expected for ods_code in ods_codes}

    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ORGANISATION, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=EnumAbstractionLevel.ORGANISATION,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{EnumAbstractionLevel.ORGANISATION.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_trust_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at trust level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # ParentOrganisation_ODSCode
    abstraction_codes = ["RGT", "RQM"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}
    abstraction_level = EnumAbstractionLevel.TRUST

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.TRUST, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_icb_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at icb level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # integrated_care_board__ODS_ICB_Code
    abstraction_codes = ["QUE", "QRV"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}
    abstraction_level = EnumAbstractionLevel.ICB

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ICB, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_nhs_region_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at nhs region level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # nhs_region__NHS_Region_Code
    abstraction_codes = ["Y61", "Y56"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}
    abstraction_level = EnumAbstractionLevel.NHS_REGION

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.NHS_REGION, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_open_uk_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at OPENUK level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # openuk_network__OPEN_UK_Network_Code
    abstraction_codes = ["EPEN", "NTPEN"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}
    abstraction_level = EnumAbstractionLevel.OPEN_UK

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.OPEN_UK, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_country_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at country level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # ons_region__ons_country__Country_ONS_Code
    abstraction_codes = ["E92000001", "W92000004"]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}
    abstraction_level = EnumAbstractionLevel.COUNTRY

    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.COUNTRY, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[code]


@pytest.mark.django_db
def test_update_kpi_aggregation_model_organisation_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level`. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.ORGANISATION
    abstractions = [
        Organisation.objects.get(ODSCode=abstraction_code)
        for abstraction_code in ("RGT01", "7A6AV")
    ]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ORGANISATION, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6,
        kpi_value_counts=value_counts,
        abstraction_level=EnumAbstractionLevel.ORGANISATION,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = OrganisationKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_trust_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but on Trust level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.TRUST
    abstractions = [
        Organisation.objects.filter(ParentOrganisation_ODSCode=abstraction_code).first()
        for abstraction_code in ("RGT", "7A6")
    ]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.TRUST, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6,
        kpi_value_counts=value_counts,
        abstraction_level=EnumAbstractionLevel.TRUST,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = TrustKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_icb_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at icb level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.ICB

    expected_scores = {
        IntegratedCareBoardEntity.objects.get(ODS_ICB_Code="QUE"): {
            "ecg_passed": 10,
            "ecg_total_eligible": 20,
            "ecg_ineligible": 10,
            "ecg_incomplete": 10,
            "mental_health_support_passed": 10,
            "mental_health_support_total_eligible": 20,
            "mental_health_support_ineligible": 10,
            "mental_health_support_incomplete": 10,
        }
    }

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=abstraction_level, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6, kpi_value_counts=value_counts, abstraction_level=abstraction_level
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = ICBKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_nhs_region_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at nhs region level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.NHS_REGION
    abstractions = [
        NHSRegionEntity.objects.get(NHS_Region_Code=abstraction_code)
        for abstraction_code in ("Y61", "7A6")
    ]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.NHS_REGION, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6,
        kpi_value_counts=value_counts,
        abstraction_level=EnumAbstractionLevel.NHS_REGION,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = NHSRegionKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_open_uk_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at openuk level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.OPEN_UK
    abstractions = [
        OPENUKNetworkEntity.objects.get(OPEN_UK_Network_Code=abstraction_code)
        for abstraction_code in ("EPEN", "SWEP")
    ]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.OPEN_UK, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6,
        kpi_value_counts=value_counts,
        abstraction_level=EnumAbstractionLevel.OPEN_UK,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = OpenUKKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_country_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at country level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]
    abstraction_level = EnumAbstractionLevel.COUNTRY
    abstractions = [
        ONSCountryEntity.objects.get(Country_ONS_Code=abstraction_code)
        for abstraction_code in ("E92000001", "W92000004")
    ]
    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.COUNTRY, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6,
        kpi_value_counts=value_counts,
        abstraction_level=EnumAbstractionLevel.COUNTRY,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = CountryKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_get_filtered_cases_queryset_all_levels(e12_case_factory):
    """Testing the `get_filtered_cases_queryset_for` returns the correct count for filtered cases. Specifically ensuring Welsh hospitals ignored for ICB abstraction."""

    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    # Generate test cases
    expected_first_names = []
    ods_codes = ["RGT01", "7A6AV"]
    for code in ods_codes:
        org = Organisation.objects.get(ODSCode=code)

        # Used to filter these Cases
        expected_first_names.append(f"temp_{org.OrganisationName}")

        e12_case_factory.create_batch(
            10,
            organisations__organisation=org,
            first_name=f"temp_{org.OrganisationName}",
        )

    # Universal abstractions
    for ABSTRACTION_LEVEL in [
        EnumAbstractionLevel.ORGANISATION,
        EnumAbstractionLevel.TRUST,
        EnumAbstractionLevel.NHS_REGION,
        EnumAbstractionLevel.OPEN_UK,
        EnumAbstractionLevel.COUNTRY,
    ]:
        output_filtered_cases = get_filtered_cases_queryset_for(
            abstraction_level=ABSTRACTION_LEVEL, cohort=6
        )

        assert (
            20 == output_filtered_cases.count()
        ), f"Did not output correct COUNT(filtered_cases) for {ABSTRACTION_LEVEL}"

    # Distinction for Welsh hospitals
    for ABSTRACTION_LEVEL in [
        EnumAbstractionLevel.ICB,
    ]:
        output_filtered_cases = get_filtered_cases_queryset_for(
            abstraction_level=ABSTRACTION_LEVEL, cohort=6
        )

        assert (
            10 == output_filtered_cases.count()
        ), f"Did not output correct COUNT(filtered_cases) for {ABSTRACTION_LEVEL}"


@pytest.mark.django_db
def test_get_filtered_cases_queryset_organisation_level_includes_only_specified_cohort(
    e12_case_factory,
):
    """Testing the `get_filtered_cases_queryset_for` function ignores kids who are from different cohort to specificed `cohort` arg. Here, all test kids are part of Cohort 4, but we request Cohort 6 Cases."""

    # Ensure Case db empty for this test
    Registration.objects.all().delete()
    Case.objects.all().delete()

    # Generate test cases
    expected_first_names = []
    ods_codes = ["RGT01", "7A6AV"]
    for code in ods_codes:
        org = Organisation.objects.get(ODSCode=code)

        # Used to filter these Cases
        expected_first_names.append(f"temp_{org.OrganisationName}")

        e12_case_factory.create_batch(
            10,
            organisations__organisation=org,
            first_name=f"temp_{org.OrganisationName}",
            registration__registration_date=date(2021, 1, 1),
        )

    output_filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ORGANISATION, cohort=6
    )

    assert 0 == output_filtered_cases.count()


@pytest.mark.django_db
def test_debug(e12_case_factory):
    """debug"""
    pass
