"""
Tests for the recalculate_postcode_data management command and update_location_for_case().

By default the command only fills in a missing IMD quintile or location. With
--rebuild it recalculates both for every case in scope.

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
from epilepsy12.general_functions.postcode import update_location_for_case

IMD_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.imd_for_postcode"
COUNTRY_PATCH = "epilepsy12.general_functions.index_multiple_deprivation.country_boundary_identifier_for_postcode"
CASE_COORDS_PATCH = "epilepsy12.models_folder.case.coordinates_for_postcode"
UPDATE_COORDS_PATCH = "epilepsy12.general_functions.postcode.coordinates_for_postcode"

COORDINATES = (-0.1234, 51.5678)
OTHER_COORDINATES = (-1.5, 53.8)

# Cohort 7
COHORT_7_DATE = date(2024, 6, 1)
# Cohort 8
COHORT_8_DATE = date(2025, 6, 1)


@pytest.fixture
def mock_apis():
    """Mocks every external call. Cases get COORDINATES and IMD 2 on save."""
    with patch(COUNTRY_PATCH, return_value="E92000001") as country, patch(
        IMD_PATCH, return_value=2
    ) as imd, patch(CASE_COORDS_PATCH, return_value=COORDINATES) as case_coords, patch(
        UPDATE_COORDS_PATCH, return_value=OTHER_COORDINATES
    ) as update_coords:
        yield {
            "country": country,
            "imd": imd,
            "case_coords": case_coords,
            "update_coords": update_coords,
        }


def _clear_location(case):
    Case.objects.filter(pk=case.pk).update(location_wgs84=None, location_bng=None)
    case.refresh_from_db()


def _clear_imd(case):
    Case.objects.filter(pk=case.pk).update(index_of_multiple_deprivation_quintile=None)
    case.refresh_from_db()


def _cohort(case):
    return case.registration.audit_period.cohort_number


# ── update_location_for_case ────────────────────────────────────────────────


@pytest.mark.django_db
def test_update_location_fills_missing_and_persists(mock_apis, e12_case_factory):
    case = e12_case_factory(postcode="WC1X8SH")
    _clear_location(case)

    assert update_location_for_case(case) == "filled"

    mock_apis["update_coords"].assert_called_once_with(postcode="WC1X8SH")
    saved = Case.objects.get(pk=case.pk)
    assert saved.location_wgs84.coords == pytest.approx(OTHER_COORDINATES)
    assert saved.location_wgs84.srid == 4326
    assert saved.location_bng is not None
    assert saved.location_bng.srid == 27700
    assert case.location_wgs84 == saved.location_wgs84


@pytest.mark.django_db
def test_update_location_leaves_existing_location_by_default(
    mock_apis, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    assert case.location_wgs84 is not None

    assert update_location_for_case(case) == "present"
    mock_apis["update_coords"].assert_not_called()


@pytest.mark.django_db
def test_update_location_rebuild_replaces_existing_location(
    mock_apis, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    assert case.location_wgs84.coords == pytest.approx(COORDINATES)

    assert update_location_for_case(case, rebuild=True) == "filled"
    assert Case.objects.get(pk=case.pk).location_wgs84.coords == pytest.approx(
        OTHER_COORDINATES
    )


@pytest.mark.django_db
def test_update_location_rebuild_keeps_existing_location_when_lookup_fails(
    mock_apis, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    mock_apis["update_coords"].return_value = None

    assert update_location_for_case(case, rebuild=True) == "failed"
    assert Case.objects.get(pk=case.pk).location_wgs84.coords == pytest.approx(
        COORDINATES
    )


@pytest.mark.django_db
def test_update_location_reports_failed_lookup(mock_apis, e12_case_factory):
    case = e12_case_factory(postcode="WC1X8SH")
    _clear_location(case)
    mock_apis["update_coords"].return_value = None

    assert update_location_for_case(case) == "failed"
    assert Case.objects.get(pk=case.pk).location_wgs84 is None


@pytest.mark.django_db
@pytest.mark.parametrize("postcode", ["ZZ993CZ", "JE11AA", None])
def test_update_location_skips_unusable_postcodes(
    mock_apis, postcode, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    Case.objects.filter(pk=case.pk).update(
        postcode=postcode, location_wgs84=None, location_bng=None
    )
    case.refresh_from_db()

    assert update_location_for_case(case) == "skipped"
    assert update_location_for_case(case, rebuild=True) == "skipped"
    mock_apis["update_coords"].assert_not_called()


@pytest.mark.django_db
def test_update_location_rebuild_clears_location_for_unusable_postcode(
    mock_apis, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH")
    Case.objects.filter(pk=case.pk).update(postcode="ZZ993CZ")
    case.refresh_from_db()
    assert case.location_wgs84 is not None

    # Not rebuilding: the location is left alone.
    assert update_location_for_case(case) == "present"

    assert update_location_for_case(case, rebuild=True) == "cleared"
    saved = Case.objects.get(pk=case.pk)
    assert saved.location_wgs84 is None
    assert saved.location_bng is None
    mock_apis["update_coords"].assert_not_called()


# ── recalculate_postcode_data command: missing values only (default) ────────


@pytest.mark.django_db
def test_command_fills_only_missing_values_for_cohort(mock_apis, e12_case_factory):
    complete = e12_case_factory(
        postcode="SW1A1AA", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    missing_location = e12_case_factory(
        postcode="WC1X8SH", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    missing_imd = e12_case_factory(
        postcode="N19GU", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    other_cohort = e12_case_factory(
        postcode="EC1A1BB", registration__first_paediatric_assessment_date=COHORT_8_DATE
    )
    _clear_location(missing_location)
    _clear_imd(missing_imd)
    _clear_location(other_cohort)
    _clear_imd(other_cohort)
    cohort = _cohort(complete)
    assert _cohort(other_cohort) != cohort

    mock_apis["imd"].reset_mock()
    mock_apis["imd"].return_value = 4
    stdout = StringIO()
    call_command("recalculate_postcode_data", "--cohort", str(cohort), stdout=stdout)

    # Only the case missing IMD is looked up for IMD, and only the case
    # missing a location is looked up for location.
    assert [c.args for c in mock_apis["imd"].call_args_list] == [("N19GU",)]
    mock_apis["update_coords"].assert_called_once_with(postcode="WC1X8SH")

    assert Case.objects.get(pk=complete.pk).index_of_multiple_deprivation_quintile == 2
    assert (
        Case.objects.get(pk=missing_location.pk).index_of_multiple_deprivation_quintile
        == 2
    )
    assert Case.objects.get(pk=missing_location.pk).location_wgs84 is not None
    assert (
        Case.objects.get(pk=missing_imd.pk).index_of_multiple_deprivation_quintile == 4
    )
    # Out of scope
    assert Case.objects.get(pk=other_cohort.pk).location_wgs84 is None
    assert (
        Case.objects.get(pk=other_cohort.pk).index_of_multiple_deprivation_quintile
        is None
    )

    output = stdout.getvalue()
    assert "2 of 3 case(s) to process" in output
    assert "IMD: 1 recalculated" in output
    assert "Locations: 1 filled in" in output


@pytest.mark.django_db
def test_command_rerun_after_completion_does_nothing(mock_apis, e12_case_factory):
    case = e12_case_factory(
        postcode="WC1X8SH", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    _clear_location(case)
    _clear_imd(case)

    call_command(
        "recalculate_postcode_data", "--cohort", str(_cohort(case)), stdout=StringIO()
    )
    mock_apis["imd"].reset_mock()
    mock_apis["update_coords"].reset_mock()

    stdout = StringIO()
    call_command(
        "recalculate_postcode_data", "--cohort", str(_cohort(case)), stdout=stdout
    )

    mock_apis["imd"].assert_not_called()
    mock_apis["update_coords"].assert_not_called()
    assert "0 of 1 case(s) to process" in stdout.getvalue()


@pytest.mark.django_db
def test_command_all_fills_locations_for_unregistered_cases(
    mock_apis, e12_case_factory
):
    case = e12_case_factory(postcode="WC1X8SH", registration=None)
    _clear_location(case)

    call_command("recalculate_postcode_data", "--all", stdout=StringIO())

    assert Case.objects.get(pk=case.pk).location_wgs84 is not None


# ── recalculate_postcode_data command: --rebuild ────────────────────────────


@pytest.mark.django_db
def test_command_rebuild_recalculates_every_case(mock_apis, e12_case_factory):
    first = e12_case_factory(
        postcode="SW1A1AA", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    second = e12_case_factory(
        postcode="WC1X8SH", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    _clear_location(second)

    mock_apis["imd"].reset_mock()
    mock_apis["imd"].return_value = 5
    stdout = StringIO()
    call_command(
        "recalculate_postcode_data",
        "--cohort",
        str(_cohort(first)),
        "--rebuild",
        stdout=stdout,
    )

    assert mock_apis["imd"].call_count == 2
    assert mock_apis["update_coords"].call_count == 2
    for case in (first, second):
        saved = Case.objects.get(pk=case.pk)
        assert saved.index_of_multiple_deprivation_quintile == 5
        assert saved.location_wgs84.coords == pytest.approx(OTHER_COORDINATES)
    assert "2 of 2 case(s) to process" in stdout.getvalue()


# ── recalculate_postcode_data command: --dry-run ────────────────────────────


@pytest.mark.django_db
@pytest.mark.parametrize(
    "extra_args, expected",
    [
        ([], "Would look up IMD for 1 case(s) and location for 1 case(s)"),
        (["--rebuild"], "Would look up IMD for 2 case(s) and location for 2 case(s)"),
    ],
)
def test_command_dry_run_makes_no_api_calls(
    mock_apis, extra_args, expected, e12_case_factory
):
    missing_location = e12_case_factory(
        postcode="WC1X8SH", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    missing_imd = e12_case_factory(
        postcode="SW1A1AA", registration__first_paediatric_assessment_date=COHORT_7_DATE
    )
    _clear_location(missing_location)
    _clear_imd(missing_imd)
    cohort = _cohort(missing_location)

    mock_apis["imd"].reset_mock()
    mock_apis["country"].reset_mock()
    stdout = StringIO()
    call_command(
        "recalculate_postcode_data",
        "--cohort",
        str(cohort),
        "--dry-run",
        *extra_args,
        stdout=stdout,
    )

    mock_apis["imd"].assert_not_called()
    mock_apis["country"].assert_not_called()
    mock_apis["update_coords"].assert_not_called()
    output = stdout.getvalue()
    assert "[DRY RUN]" in output
    assert "1 are missing IMD and 1 are missing a location" in output
    assert expected in output
