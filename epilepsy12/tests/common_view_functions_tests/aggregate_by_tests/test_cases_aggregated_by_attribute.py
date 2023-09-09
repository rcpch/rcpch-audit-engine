# python imports
import pytest

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_ethnicity,
)
from epilepsy12.models import (
    Organisation,
)
from epilepsy12.constants import (
    SEX_TYPE,
    DEPRIVATION_QUINTILES,
    ETHNICITIES,
)


@pytest.mark.django_db
def test_cases_aggregated_by_sex(e12_case_factory):
    """Tests the cases_aggregated_by_sex fn returns correct count.

    NOTE: There is already 1 seeded Case in the test db. In this test setup, we seed 10 children per SEX_TYPE (n=4).

    Thus expected total count is 10 for each sex, except Male, which is 11.
    """

    # define constants
    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
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
        ods_code="RQM01",
        trust__ods_code="RQM",
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
        ods_code="RP401",
        trust__ods_code="RP4",
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
