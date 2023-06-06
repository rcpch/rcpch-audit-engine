"""Tests for aggregate_by.py functions.
"""

# python imports
import pytest

# django imports

# E12 imports
from epilepsy12.common_view_functions.aggregate_by import (
    cases_aggregated_by_sex,
    cases_aggregated_by_deprivation_score,
)
from epilepsy12.models import Organisation
from epilepsy12.constants.common import SEX_TYPE, DEPRIVATION_QUINTILES


@pytest.mark.django_db
def test_cases_aggregated_by_sex_correct_output(e12_case_factory, e12_site_factory):
    """Tests the cases_aggregated_by_sex fn returns correct count."""
    # Create 10 cases of each available sex type
    for sex_type in SEX_TYPE:
        # set an organisation constant
        organisation = Organisation.objects.first()

        # For each sex, assign 10 cases
        for _ in range(10):
            case = e12_case_factory.create(sex=sex_type[0], registration=None)

            # clean default organisations created in factory
            case.organisations.clear()

            # relate to organisation constant
            case.organisations.add(
                e12_site_factory(case=case, organisation=organisation).organisation
            )
            case.save()

    total_count = cases_aggregated_by_sex(selected_organisation=organisation).count()
    matching_count = (
        cases_aggregated_by_sex(selected_organisation=organisation)
        .filter(sexes=10)
        .count()
    )

    assert (
        total_count == matching_count
    ), f"Not returning correct count. {total_count} should equal {matching_count}"


@pytest.mark.django_db
def test_cases_aggregated_by_deprivation_score(e12_case_factory, e12_site_factory):
    """Tests the cases_aggregated_by_deprivation_score fn returns correct count."""

    # Loop through each deprivation quintile
    for deprivation_type in DEPRIVATION_QUINTILES:
        # set an organisation constant
        organisation = Organisation.objects.first()

        # For each deprivation, assign 10 cases
        for _ in range(10):
            case = e12_case_factory.create(
                index_of_multiple_deprivation_quintile=deprivation_type[1],
                registration=None,
            )

            # clean default organisations created in factory
            case.organisations.clear()

            # relate to organisation constant
            case.organisations.add(
                e12_site_factory(case=case, organisation=organisation).organisation
            )
            case.save()

    total_count = cases_aggregated_by_deprivation_score(
        selected_organisation=organisation
    ).count()

    matching_count = (
        cases_aggregated_by_deprivation_score(selected_organisation=organisation)
        .filter(cases_aggregated_by_deprivation=10)
        .count()
    )

    assert (
        total_count == matching_count
    ), f"Not returning correct count. {total_count=} should equal {matching_count=}"
