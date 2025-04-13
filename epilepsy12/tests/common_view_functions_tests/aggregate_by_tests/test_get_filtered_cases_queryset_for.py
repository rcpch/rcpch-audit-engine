"""Shell code to quickly access Orgs within same abstraction
from django.db.models import Count
from epilepsy12.models import Organisation

a = Organisation.objects.get(ods_code="RP401")

Organisation.objects.exclude(
            # ods_code=a.ods_code,
            # trust__ods_code=a.trust__ods_code,
            # integrated_care_board=a.integrated_care_board,
            # nhs_region=a.nhs_region,
            # openuk_network=a.openuk_network,
        ).filter(openuk_network=a.openuk_network).values_list("ods_code", "name")
"""

# python imports
import pytest
from datetime import date
from unittest.mock import patch

# 3rd party imports
from django.db.models import Count

# E12 imports
from epilepsy12.common_view_functions import (
    get_filtered_cases_queryset_for,
)
from epilepsy12.models import Organisation, Registration
from epilepsy12.constants import (
    EnumAbstractionLevel,
)

from .helpers import _clean_cases_from_test_db, _register_cases_in_organisation


@pytest.mark.parametrize(
    "abstraction_level, ODSCodes, expected_count",
    [
        (EnumAbstractionLevel.ORGANISATION, ("RGT01", "7A6AV"), (10, 10)),
        (
            EnumAbstractionLevel.TRUST,
            ("RP401", "RP416", "7A6AV"),
            (20, 20, 0),
        ),  # Welsh have no Trust
        (
            EnumAbstractionLevel.LOCAL_HEALTH_BOARD,
            ("RP401", "RP416", "7A6AV"),
            (0, 0, 10),
        ),  # English have no LHB
        (
            EnumAbstractionLevel.ICB,
            ("RGT01", "RGN90", "7A6AV"),
            (20, 20, 0),
        ),  # Welsh have no ICB
        (
            EnumAbstractionLevel.NHS_ENGLAND_REGION,
            ("RGT01", "RGN90", "7A6AV"),
            (20, 20, 0),
        ),  # Welsh have no NHS_ENGLAND_REGION
        (EnumAbstractionLevel.OPEN_UK, ("RGT01", "RGN90", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.COUNTRY, ("RGT01", "RGN90", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.NATIONAL, ("RGT01", "RGN90", "7A6AV"), (30, 30, 30)),
    ],
)
@pytest.mark.django_db
def test_get_filtered_cases_queryset_for_returns_correct_count(
    abstraction_level,
    ODSCodes,
    expected_count,
    e12_case_factory,
):
    """Testing the `get_filtered_cases_queryset_for` returns the correct expected_count for filtered cases.
    Not the mocked first paediatric assessment date is 1/1/23 so all will have completed their first year of care
    For each abstraction, 20 Cases are registered in the same abstraction level (all English organisations, split between 2 organisations), and 10 Cases in Wales - so should be excluded from agg counts.
    """

    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    # Generate test cases - 10 in each ods_code given
    ods_codes = ODSCodes
    _register_cases_in_organisation(
        ods_codes=ods_codes, e12_case_factory=e12_case_factory
    )

    for ix, ods_code in enumerate(ods_codes):
        organisation = Organisation.objects.get(ods_code=ods_code)

        output = get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=abstraction_level,
            cohort=6,
        ).count()

        assert (
            output == expected_count[ix]
        ), f"""get_total_cases_registered_for_abstraction_level(
            organisation={organisation},
            abstraction_level={abstraction_level.name},
            cohort=6,
        ) should be {expected_count[ix]}"""


@pytest.mark.django_db
def test_get_filtered_cases_queryset_includes_only_specified_cohort(
    e12_case_factory,
):
    """Testing the `get_filtered_cases_queryset_for` function ignores kids who are from different cohort to specificed `cohort` arg. Here, all test kids are part of Cohort 4, but we request Cohort 6 Cases."""

    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    # Generate test cases
    org = Organisation.objects.get(ods_code="RGT01")
    e12_case_factory.create_batch(
        10,
        organisations__organisation=org,
        first_name=f"temp_{org.name}",
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )

    for abstraction_level in EnumAbstractionLevel:
        output_filtered_cases = get_filtered_cases_queryset_for(
            abstraction_level=abstraction_level, cohort=6, organisation=org
        )

        assert 0 == output_filtered_cases.count()


@patch.object(Registration, "get_current_date", return_value=date(2024, 3, 1))
@pytest.mark.django_db
def test_get_filtered_cases_queryset_includes_only_specified_cohort_that_have_completed_one_full_year(
    e12_case_factory,
):
    """Testing the `get_filtered_cases_queryset_for` function ignores kids who are from same `cohort` but did not complete 1y. Here, all test kids are part of Cohort 6, but none have completed 1 y."""

    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    # Cohort 6 includes patients who had a first assessment between 1 December 2022 and 30 November 2023. Patients will then complete their first year of care between 1 December 2023 to 30 November 2024.

    # Generate test cases
    org = Organisation.objects.get(ods_code="RGT01")
    e12_case_factory.create_batch(
        10,
        organisations__organisation=org,
        first_name=f"temp_{org.name}",
        registration__first_paediatric_assessment_date=date(
            2023, 8, 1
        ),  # cohort 6 (1/12/22-30/11/23): end of first year of care therefore 1/8/24: mocked date of 1/3/24 therefore before completion of 1y of care
    )

    for abstraction_level in EnumAbstractionLevel:
        output_filtered_cases = get_filtered_cases_queryset_for(
            abstraction_level=abstraction_level, cohort=6, organisation=org
        )

        assert 0 == output_filtered_cases.count()


@pytest.mark.django_db
def test_get_filtered_cases_queryset_for_orgs_with_null_ICB(
    e12_case_factory,
):
    """Some abstractions for organisations will be None e.g. Welsh organisations do not have an ICB; English organisations will not have a health board.

    TODO: healthboards model not yet implemented - add test once done.
    """
    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    ods_codes_where_icb_null = [
        code[0]
        for code in Organisation.objects.all()
        .values("ods_code", "name", "integrated_care_board")
        .annotate(count=Count("integrated_care_board"))
        .filter(count__lt=1)
        .values_list("ods_code")
        .distinct()
    ]

    # Generate test cases - 10 in each ods_code given
    _register_cases_in_organisation(
        ods_codes=ods_codes_where_icb_null,
        e12_case_factory=e12_case_factory,
        n_cases=10,
    )

    for ods_code in ods_codes_where_icb_null:
        # Community Paediatrics Org returning with the actual org so need to do filter.first()
        organisation = Organisation.objects.filter(
            ods_code=ods_code, active=True
        ).first()

        output = get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=EnumAbstractionLevel.ICB,
            cohort=6,
        ).count()

        assert (
            output == 0
        ), f"""(Usually Welsh) organisations with null ICB codes should not be returned from get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=EnumAbstractionLevel.ICB,
            cohort=6,
        )"""
