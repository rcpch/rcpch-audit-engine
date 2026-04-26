"""
Tests for IMD (Index of Multiple Deprivation) calculation.

IMD is calculated by recalculate_imd_for_case(), triggered via post_save
signals on Case (postcode change) and Registration (first_paediatric_assessment_date
change).  The RCPCH Census Platform API accepts a `year` parameter:
  - cohort < 8  → year=2019
  - cohort >= 8 → year=2025

All tests mock imd_for_postcode so no real network calls are made.

Cohort reference:
  Cohort 7: first_paediatric_assessment_date in Dec 2023 – Nov 2024  (year=2019)
  Cohort 8: first_paediatric_assessment_date in Dec 2024 – Nov 2025  (year=2025)
"""

# Standard imports
import pytest
from datetime import date
from unittest.mock import patch, call

# RCPCH imports
from epilepsy12.general_functions.index_multiple_deprivation import (
    recalculate_imd_for_case,
)

IMD_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.imd_for_postcode"
COORDS_PATCH = "epilepsy12.models_folder.case.coordinates_for_postcode"
COUNTRY_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.country_boundary_identifier_for_postcode"


def assert_imd_call(mock_imd, postcode, year, country_boundary_identifier=None):
    """Assert the IMD helper was called with the expected postcode/year.

    Tests accept additional country kwargs so they remain valid as the helper
    signature evolves.
    """
    args, kwargs = mock_imd.call_args

    assert args == (postcode,)
    assert kwargs.get("year") == year

    if country_boundary_identifier is not None:
        if "country" in kwargs:
            assert kwargs["country"] == country_boundary_identifier
        if "country_boundary_identifier" in kwargs:
            assert kwargs["country_boundary_identifier"] == country_boundary_identifier


# ── Correct year selection ──────────────────────────────────────────────────


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_uses_2019_for_cohort_below_8(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """Cohort 7 (assessment date in 2024) should call the API with year=2019."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 3

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),  # cohort 7
    )

    case.refresh_from_db()
    assert case.registration.cohort == 7
    assert_imd_call(
        mock_imd, "WC1X8SH", year=2019, country_boundary_identifier="E92000001"
    )
    assert case.index_of_multiple_deprivation_quintile == 3


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_uses_2025_for_cohort_8_and_above(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """Cohort 8 (assessment date in 2025) should call the API with year=2025."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 2

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2025, 3, 1),  # cohort 8
    )

    case.refresh_from_db()
    assert case.registration.cohort == 8
    assert_imd_call(
        mock_imd, "WC1X8SH", year=2025, country_boundary_identifier="E92000001"
    )
    assert case.index_of_multiple_deprivation_quintile == 2


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_recalculated_when_assessment_date_changes_cohort(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """Changing first_paediatric_assessment_date across the cohort 7→8 boundary
    should trigger a new IMD call with year=2025."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 1

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),  # cohort 7
    )

    registration = case.registration
    assert registration.cohort == 7

    # Advance into cohort 8
    mock_imd.return_value = 5
    registration.first_paediatric_assessment_date = date(2025, 3, 1)
    registration.save()

    case.refresh_from_db()
    assert case.registration.cohort == 8
    assert_imd_call(
        mock_imd, "WC1X8SH", year=2025, country_boundary_identifier="E92000001"
    )
    assert case.index_of_multiple_deprivation_quintile == 5


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="W92000004")
def test_imd_uses_2019_for_cohort_8_when_country_not_england(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """Cohort 8 should still use year=2019 outside England (e.g. Wales)."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 2

    case = e12_case_factory(
        postcode="CF10 1AA",
        registration__first_paediatric_assessment_date=date(2025, 3, 1),  # cohort 8
    )

    case.refresh_from_db()
    assert case.registration.cohort == 8
    assert_imd_call(
        mock_imd, "CF101AA", year=2019, country_boundary_identifier="W92000004"
    )
    assert case.index_of_multiple_deprivation_quintile == 2


# ── Postcode triggers ───────────────────────────────────────────────────────


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_recalculated_when_postcode_changes(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """Saving a Case with a new postcode should trigger a fresh IMD lookup."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 2

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )

    mock_imd.return_value = 4
    case.postcode = "EC1A1BB"
    case.save()

    case.refresh_from_db()
    assert_imd_call(
        mock_imd, "EC1A1BB", year=2019, country_boundary_identifier="E92000001"
    )
    assert case.index_of_multiple_deprivation_quintile == 4


# ── No-op cases ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
@patch(IMD_PATCH)
def test_imd_not_calculated_when_postcode_is_none(mock_imd, e12_case_factory):
    """A case with no postcode should never call the IMD API."""
    case = e12_case_factory(postcode=None, index_of_multiple_deprivation_quintile=None)
    mock_imd.assert_not_called()
    assert case.index_of_multiple_deprivation_quintile is None


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_not_calculated_for_unknown_postcode(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """A case with an 'unknown' placeholder postcode should not call the API."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 3

    # Start with a real postcode (triggers a call on creation)
    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )
    mock_imd.reset_mock()

    # Switch to an unknown postcode
    case.postcode = "ZZ99 3CZ"
    case.save()

    mock_imd.assert_not_called()
    case.refresh_from_db()
    assert case.index_of_multiple_deprivation_quintile is None


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_not_calculated_when_no_registration(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """recalculate_imd_for_case should be a no-op when no Registration exists."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 3

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )

    # Delete the registration, then re-fetch the case so Django's related-object
    # cache is cleared (otherwise case.registration still returns the cached instance).
    case.registration.delete()
    from epilepsy12.models import Case

    case = Case.objects.get(pk=case.pk)
    mock_imd.reset_mock()

    # Call utility directly — should exit early without calling the API
    recalculate_imd_for_case(case)
    mock_imd.assert_not_called()


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_not_calculated_when_cohort_is_none(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """recalculate_imd_for_case should be a no-op when the cohort is not yet set."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 3

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )

    # Force cohort to None without triggering signals
    from epilepsy12.models import Registration

    Registration.objects.filter(pk=case.registration.pk).update(cohort=None)
    case.registration.refresh_from_db()
    mock_imd.reset_mock()

    recalculate_imd_for_case(case)
    mock_imd.assert_not_called()


# ── Persistence ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_persisted_to_database(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """The IMD quintile returned by the API should be written to the database."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = 5

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )

    from epilepsy12.models import Case

    db_value = Case.objects.get(pk=case.pk).index_of_multiple_deprivation_quintile
    assert db_value == 5


@pytest.mark.django_db
@patch(COORDS_PATCH)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_imd_set_to_none_when_api_returns_none(
    mock_country, mock_imd, mock_coords, e12_case_factory
):
    """If the API returns None (e.g. postcode not found), IMD should be None."""
    mock_coords.return_value = (-0.1234, 51.5678)
    mock_imd.return_value = None

    case = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )

    case.refresh_from_db()
    assert case.index_of_multiple_deprivation_quintile is None
