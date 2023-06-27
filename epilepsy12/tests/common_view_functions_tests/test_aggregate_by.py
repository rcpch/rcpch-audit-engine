"""Tests for aggregate_by.py functions.
"""

# python imports
import pytest
from datetime import date

# 3rd party imports
from django.contrib.gis.db.models import (
    Count,
    When,
    ExpressionWrapper,
    F,
    Value,
    PositiveSmallIntegerField,
    Case as DJANGO_CASE,
)

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
from epilepsy12.constants import SEX_TYPE, DEPRIVATION_QUINTILES, ETHNICITIES
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
    GOSH = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    # Loop through each deprivation quintile
    for deprivation_type in DEPRIVATION_QUINTILES.deprivation_quintiles:
        # For each deprivation, assign 10 cases, add to cases_list
        e12_case_factory.create_batch(
            size=10,
            index_of_multiple_deprivation_quintile=deprivation_type,
            registration=None,  # ensure related audit factories not generated
            organisations__organisation=GOSH,
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
            "cases_aggregated_by_deprivation": 11, # THIS IS 11 AS THERE IS ALREADY 1 SEEDED CASE IN TEST Db WITH THIS IMD
            "index_of_multiple_deprivation_quintile_display_str": "Not known",
        },
    ]

    cases_queryset = cases_aggregated_by_deprivation_score(GOSH)

    for ix, aggregate in enumerate(cases_queryset):
        

        assert aggregate == expected_counts[ix], f"Expected aggregate count for test_cases_aggregated_by_deprivation_score not matching output."


@pytest.mark.django_db
def test_cases_aggregated_by_ethnicity(e12_case_factory):
    """Tests the cases_aggregated_by_ethnicity fn returns correct count."""

    # define constants
    ORGANISATION = Organisation.objects.first()

    # Loop through each ethnicity
    cases_list = []
    for ethnicity_type in ETHNICITIES:
        # For each ethnicity, build 10 cases, and append to cases_list
        for _ in range(10):
            case = e12_case_factory.build(
                nhs_number=generate_nhs_number(),
                ethnicity=ethnicity_type[0],
                registration=None,  # ensure related audit factories not generated
                organisations__organisation=ORGANISATION,
            )
            cases_list.append(case)

    # single SQL INSERT to save all cases
    Case.objects.bulk_create(cases_list)

    total_count = cases_aggregated_by_ethnicity(
        selected_organisation=ORGANISATION
    ).count()

    matching_count = (
        cases_aggregated_by_ethnicity(selected_organisation=ORGANISATION)
        .filter(ethnicities=10)
        .count()
    )

    assert (
        total_count == matching_count
    ), f"Not returning correct count. {total_count=} should equal {matching_count=}"


@pytest.mark.django_db
def test_aggregate_all_eligible_kpi_fields_correct_count(e12_case_factory):
    """Tests the aggregate_all_eligible_kpi_fields fn returns correct count of KPIs."""

    # define constants
    ORGANISATION = Organisation.objects.first()
    COHORT = 6

    for _ in range(10):
        e12_case_factory.create(
            organisations__organisation=ORGANISATION, nhs_number=generate_nhs_number()
        )

    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=ORGANISATION,
        cohort=COHORT,
        case_complete=False,
        abstraction_level="organisation",
    )

    aggregated_kpis = aggregate_all_eligible_kpi_fields(organisation_level)

    total_count_kpis = -1  # start at -1 to exclude "total_number_of_cases"
    for key in aggregated_kpis:
        if "total" in key:
            total_count_kpis += 1

    assert total_count_kpis == 21


@pytest.mark.skip(reason="unfinished test")
@pytest.mark.django_db
def test_aggregate_all_eligible_kpi_fields_correct_kpi_scoring(e12_case_factory):
    """Tests the aggregate_all_eligible_kpi_fields fn returns scoring of KPIs."""

    # define constants
    ORGANISATION = Organisation.objects.first()

    # create a KPI object
    kpi_metric_eligible_3_5_object = KPIMetric(
        eligible_kpi_3_5=True, eligible_kpi_6_8_10=False
    )

    # generate answer set for e12_case_factory constructor
    answers_eligible_3_5 = kpi_metric_eligible_3_5_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_3="PASS",
        kpi_4="INELIGIBLE",
        kpi_5="FAIL",
        kpi_7="PASS",
        kpi_9="PASS",
    )

    case = e12_case_factory.create(
        organisations__organisation=ORGANISATION,
        # feed in values for eligible
        **answers_eligible_3_5,
    )

    registration = Registration.objects.get(case=case)

    calculate_kpis(registration)

    kpi = KPI.objects.get(pk=registration.pk)

    for attr, val in kpi.get_kpis().items():
        print(f"{attr}:{val}")
