# python imports
import pytest
import random
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

from .helpers import _clean_cases_from_test_db


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
