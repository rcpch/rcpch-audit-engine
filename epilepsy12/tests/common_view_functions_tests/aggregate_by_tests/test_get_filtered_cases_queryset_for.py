"""Shell code to quickly access Orgs within same abstraction
from django.db.models import Count
from epilepsy12.models import Organisation

a = Organisation.objects.get(ODSCode="RP401")

Organisation.objects.exclude(
            # ODSCode=a.ODSCode,
            # ParentOrganisation_ODSCode=a.ParentOrganisation_ODSCode,
            # integrated_care_board=a.integrated_care_board,
            # nhs_region=a.nhs_region,
            # openuk_network=a.openuk_network,
        ).filter(openuk_network=a.openuk_network).values_list("ODSCode", "OrganisationName")
"""

# python imports
import pytest
from datetime import date

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    get_filtered_cases_queryset_for,
)
from epilepsy12.models import (
    Organisation,
    Case,
    Registration,
)
from epilepsy12.constants import (
    EnumAbstractionLevel,
)

from .helpers import _clean_cases_from_test_db, _register_cases_in_organisation


@pytest.mark.parametrize(
    "abstraction_level, ODSCodes, expected_count",
    [
        (EnumAbstractionLevel.ORGANISATION, ("RGT01", "7A6AV"), (10, 10)),
        (EnumAbstractionLevel.TRUST, ("RP401", "RP416", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.ICB, ("RGT01", "RYVD9", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.NHS_REGION, ("RP401", "RQM01", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.OPEN_UK, ("RP401", "RP416", "7A6AV"), (20, 20, 10)),
        (EnumAbstractionLevel.COUNTRY, ("RP401", "RP416", "7A6AV"), (20, 20, 10)),
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

    For each abstraction, Cases are registered in the same abstraction level (all English organisations), and 10 Cases in Wales - so should be excluded from agg counts.
    """

    # Ensure Case db empty for this test
    _clean_cases_from_test_db()

    # Generate test cases - 10 in each ODSCode given
    ods_codes = ODSCodes
    _register_cases_in_organisation(
        ods_codes=ods_codes, e12_case_factory=e12_case_factory
    )

    for ix, ods_code in enumerate(ods_codes):
        organisation = Organisation.objects.get(ODSCode=ods_code)

        output = get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=abstraction_level,
            cohort=6,
        ).count()

        assert (
            output == expected_count[ix]
        ), f"""get_total_cases_registered_for_abstraction_level(
            organisation={organisation},
            abstraction_level={abstraction_level},
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
    org = Organisation.objects.get(ODSCode="RGT01")
    e12_case_factory.create_batch(
        10,
        organisations__organisation=org,
        first_name=f"temp_{org.OrganisationName}",
        registration__registration_date=date(2021, 1, 1),
    )

    for abstraction_level in EnumAbstractionLevel:
        output_filtered_cases = get_filtered_cases_queryset_for(
            abstraction_level=abstraction_level, cohort=6, organisation=org
        )

        assert 0 == output_filtered_cases.count()
