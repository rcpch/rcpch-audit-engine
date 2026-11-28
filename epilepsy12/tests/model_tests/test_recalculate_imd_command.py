"""
Tests for the recalculate_imd management command and fill_missing_location_for_case().

The command recalculates the IMD quintile for every case in scope, and fills in
location_wgs84 / location_bng only for cases missing them.

All external calls are mocked so no real network calls are made.
"""

# Standard imports
from datetime import date
from io import StringIO
from unittest.mock import patch

# Third party imports
import pytest
from django.contrib.gis.geos import Point
from django.core.management import call_command

# RCPCH imports
from epilepsy12.models import Case
from epilepsy12.general_functions.postcode import fill_missing_location_for_case

IMD_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.imd_for_postcode"
COUNTRY_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.country_boundary_identifier_for_postcode"
CASE_COORDS_PATCH = "epilepsy12.models_folder.case.coordinates_for_postcode"
FILL_COORDS_PATCH = "epilepsy12.general_functions.postcode.coordinates_for_postcode"

COORDINATES = (-0.1234, 51.5678)


def _clear_location(case):
    Case.objects.filter(pk=case.pk).update(location_wgs84=None, location_bng=None)
    case.refresh_from_db()


# ── fill_missing_location_for_case ──────────────────────────────────────────


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH, return_value=COORDINATES)
@patch(CASE_COORDS_PATCH, return_value=None)
@patch(IMD_PATCH, return_value=3)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_fill_missing_location_fills_and_persists(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    # The lookup on save failed, so the case has no location.
    assert case.location_wgs84 is None

    assert fill_missing_location_for_case(case) == "filled"

    mock_fill_coords.assert_called_once_with(postcode="WC1X8SH")
    saved = Case.objects.get(pk=case.pk)
    assert saved.location_wgs84.coords == pytest.approx(COORDINATES)
    assert saved.location_wgs84.srid == 4326
    assert saved.location_bng is not None
    assert saved.location_bng.srid == 27700
    assert case.location_wgs84 == saved.location_wgs84


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH)
@patch(CASE_COORDS_PATCH, return_value=COORDINATES)
@patch(IMD_PATCH, return_value=3)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_fill_missing_location_leaves_existing_location(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    assert case.location_wgs84 is not None

    assert fill_missing_location_for_case(case) == "present"
    mock_fill_coords.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("postcode", ["ZZ993CZ", "JE11AA", None])
@patch(FILL_COORDS_PATCH)
@patch(CASE_COORDS_PATCH, return_value=None)
@patch(IMD_PATCH, return_value=None)
@patch(COUNTRY_PATCH, return_value=None)
def test_fill_missing_location_skips_unusable_postcodes(
    mock_country,
    mock_imd,
    mock_case_coords,
    mock_fill_coords,
    postcode,
    e12_case_factory,
):
    case = e12_case_factory(postcode="WC1X8SH")
    Case.objects.filter(pk=case.pk).update(
        postcode=postcode, location_wgs84=None, location_bng=None
    )
    case.refresh_from_db()

    assert fill_missing_location_for_case(case) == "skipped"
    mock_fill_coords.assert_not_called()


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH, return_value=None)
@patch(CASE_COORDS_PATCH, return_value=None)
@patch(IMD_PATCH, return_value=3)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_fill_missing_location_reports_failed_lookup(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")

    assert fill_missing_location_for_case(case) == "failed"
    assert Case.objects.get(pk=case.pk).location_wgs84 is None


# ── recalculate_imd command ─────────────────────────────────────────────────


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH, return_value=COORDINATES)
@patch(CASE_COORDS_PATCH, return_value=COORDINATES)
@patch(IMD_PATCH)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_command_recalculates_imd_and_fills_missing_locations_for_cohort(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    mock_imd.return_value = 2
    # Cohort 7
    missing = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )
    present = e12_case_factory(
        postcode="SW1A1AA",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )
    # Cohort 8, out of scope
    other_cohort = e12_case_factory(
        postcode="EC1A1BB",
        registration__first_paediatric_assessment_date=date(2025, 6, 1),
    )
    _clear_location(missing)
    _clear_location(other_cohort)
    cohort = missing.registration.audit_period.cohort_number
    assert other_cohort.registration.audit_period.cohort_number != cohort

    mock_imd.reset_mock()
    mock_imd.return_value = 4
    stdout = StringIO()
    call_command("recalculate_imd", "--cohort", str(cohort), stdout=stdout)

    assert mock_imd.call_count == 2
    mock_fill_coords.assert_called_once_with(postcode="WC1X8SH")

    assert Case.objects.get(pk=missing.pk).location_wgs84 is not None
    assert Case.objects.get(pk=missing.pk).index_of_multiple_deprivation_quintile == 4
    assert Case.objects.get(pk=present.pk).index_of_multiple_deprivation_quintile == 4
    assert Case.objects.get(pk=other_cohort.pk).location_wgs84 is None
    assert (
        Case.objects.get(pk=other_cohort.pk).index_of_multiple_deprivation_quintile == 2
    )

    output = stdout.getvalue()
    assert "Locations: 1 filled in, 0 lookups failed" in output
    assert "IMD: 2 recalculated" in output


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH, return_value=COORDINATES)
@patch(CASE_COORDS_PATCH, return_value=COORDINATES)
@patch(IMD_PATCH, return_value=2)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_command_all_fills_locations_for_unregistered_cases(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH", registration=None)
    _clear_location(case)

    call_command("recalculate_imd", "--all", stdout=StringIO())

    assert Case.objects.get(pk=case.pk).location_wgs84 is not None


@pytest.mark.django_db
@patch(FILL_COORDS_PATCH)
@patch(CASE_COORDS_PATCH, return_value=COORDINATES)
@patch(IMD_PATCH, return_value=2)
@patch(COUNTRY_PATCH, return_value="E92000001")
def test_command_dry_run_makes_no_api_calls(
    mock_country, mock_imd, mock_case_coords, mock_fill_coords, e12_case_factory
):
    fillable = e12_case_factory(
        postcode="WC1X8SH",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )
    e12_case_factory(
        postcode="SW1A1AA",
        registration__first_paediatric_assessment_date=date(2024, 6, 1),
    )
    _clear_location(fillable)
    cohort = fillable.registration.audit_period.cohort_number

    mock_imd.reset_mock()
    mock_country.reset_mock()
    stdout = StringIO()
    call_command("recalculate_imd", "--cohort", str(cohort), "--dry-run", stdout=stdout)

    mock_imd.assert_not_called()
    mock_country.assert_not_called()
    mock_fill_coords.assert_not_called()
    assert (
        f"[DRY RUN] cohort {cohort}: 2 case(s) would have IMD recalculated. "
        "1 case(s) are missing a location, of which 1 would be looked up"
    ) in stdout.getvalue()
