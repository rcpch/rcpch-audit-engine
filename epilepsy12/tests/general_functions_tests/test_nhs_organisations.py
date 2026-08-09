"""
Tests for the RCPCH NHS Organisations API client
(``epilepsy12/general_functions/nhs_organisations.py``).

The client is a thin wrapper around ``requests.get`` against the
``RCPCH_NHS_ORGANISATIONS_API_URL`` endpoint. These tests mock the HTTP layer
so no network access is required and assert that:

- the correct URL and query parameters are sent for each endpoint;
- the parsed JSON is returned unchanged;
- HTTP errors and timeouts are wrapped in ``NHSOrganisationsAPIError``;
- the 404 case from the snapshot endpoint produces a clearer error message;
- the ``organisation_geography_as_of`` wrapper delegates to the snapshot
  endpoint with the date serialised as ``YYYY-MM-DD``.

Fixtures use ``override_settings`` so the tests are independent of the
project's real ``RCPCH_NHS_ORGANISATIONS_API_URL`` setting.
"""

from datetime import date
from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError, Timeout

from epilepsy12.general_functions.nhs_organisations import (
    DEFAULT_TIMEOUT,
    NHSOrganisationsAPIError,
    get_country,
    get_integrated_care_board,
    get_local_health_board,
    get_nhs_england_region,
    get_organisation,
    get_organisation_snapshot,
    get_trust,
    list_countries,
    list_integrated_care_boards,
    list_local_health_boards,
    list_nhs_england_regions,
    list_organisations,
    list_trusts,
    organisation_geography_as_of,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


API_BASE = "https://test.rcpch.ac.uk/nhs-organisations/v1"


@pytest.fixture(autouse=True)
def override_api_url(settings):
    settings.RCPCH_NHS_ORGANISATIONS_API_URL = API_BASE


class _FakeResponse:
    """Minimal stand-in for ``requests.Response`` used by the mocks."""

    def __init__(self, json_data, status_code=200, text=""):
        self._json = json_data
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            error = HTTPError(response=self)
            raise error

    def json(self):
        return self._json


# ---------------------------------------------------------------------------
# List endpoints
# ---------------------------------------------------------------------------


def test_list_organisations_calls_correct_url_with_no_filters():
    payload = [{"ods_code": "RGT01", "name": "ADDENBROOKE'S HOSPITAL"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_organisations()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_organisations_passes_filters_as_params():
    payload = [{"ods_code": "RGT01", "name": "ADDENBROOKE'S HOSPITAL"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        list_organisations(active=True, ods_code="RGT01")

    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/",
        params={"active": True, "ods_code": "RGT01"},
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_trusts_calls_correct_url():
    payload = [{"ods_code": "RGT", "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_trusts()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/trusts/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_local_health_boards_calls_correct_url():
    payload = [{"ods_code": "7A3", "name": "Swansea Bay University Health Board"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_local_health_boards()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/local_health_boards/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_integrated_care_boards_calls_correct_url():
    payload = [{"ods_code": "QKK", "name": "NHS South East London ICB"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_integrated_care_boards()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/integrated_care_boards/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_nhs_england_regions_calls_correct_url():
    payload = [{"region_code": "Y61", "name": "East of England"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_nhs_england_regions()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/nhs_england_regions/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_countries_omits_geom_by_default():
    payload = [
        {
            "boundary_identifier": "E92000001",
            "name": "England",
            "welsh_name": "Lloegr",
            "bng_e": 394883,
            "bng_n": 370883,
            "long": -2.07811,
            "lat": 53.235,
            "globalid": "f6b76559-3626-49b8-b50b-bd15efcb0505",
        }
    ]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_countries()

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/countries/",
        params={
            "fields": (
                "boundary_identifier,name,welsh_name,bng_e,bng_n,long,lat,globalid"
            )
        },
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_countries_includes_geom_when_requested():
    payload = [
        {
            "boundary_identifier": "E92000001",
            "name": "England",
            "geom": "SRID=27700;MULTIPOLYGON (((...)))",
        }
    ]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = list_countries(include_geom=True)

    assert result == payload
    # When include_geom is True, no fields filter is sent — the API returns
    # every field including geom.
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/countries/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_list_countries_passes_filters_alongside_fields():
    payload = [{"boundary_identifier": "E92000001", "name": "England"}]
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        list_countries(name="England")

    mock_get.assert_called_once_with(
        url=f"{API_BASE}/countries/",
        params={
            "name": "England",
            "fields": (
                "boundary_identifier,name,welsh_name,bng_e,bng_n,long,lat,globalid"
            ),
        },
        timeout=DEFAULT_TIMEOUT,
    )


# ---------------------------------------------------------------------------
# Single-resource retrieve endpoints
# ---------------------------------------------------------------------------


def test_get_organisation_calls_correct_url():
    payload = {"ods_code": "RGT01", "name": "ADDENBROOKE'S HOSPITAL"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_organisation("RGT01")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/RGT01/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_trust_calls_correct_url():
    payload = {"ods_code": "RGT", "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_trust("RGT")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/trusts/RGT/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_local_health_board_calls_correct_url():
    payload = {"ods_code": "7A3", "name": "Swansea Bay University Health Board"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_local_health_board("7A3")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/local_health_boards/7A3/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_integrated_care_board_calls_correct_url():
    payload = {"ods_code": "QKK", "name": "NHS South East London ICB"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_integrated_care_board("QKK")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/integrated_care_boards/QKK/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_nhs_england_region_calls_correct_url():
    payload = {"region_code": "Y61", "name": "East of England"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_nhs_england_region("Y61")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/nhs_england_regions/Y61/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_country_omits_geom_by_default():
    payload = {
        "boundary_identifier": "E92000001",
        "name": "England",
        "welsh_name": "Lloegr",
        "bng_e": 394883,
        "bng_n": 370883,
        "long": -2.07811,
        "lat": 53.235,
        "globalid": "f6b76559-3626-49b8-b50b-bd15efcb0505",
    }
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_country("E92000001")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/countries/E92000001/",
        params={
            "fields": (
                "boundary_identifier,name,welsh_name,bng_e,bng_n,long,lat,globalid"
            )
        },
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_country_includes_geom_when_requested():
    payload = {
        "boundary_identifier": "E92000001",
        "name": "England",
        "geom": "SRID=27700;MULTIPOLYGON (((...)))",
    }
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_country("E92000001", include_geom=True)

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/countries/E92000001/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


# ---------------------------------------------------------------------------
# Snapshot / as_of endpoint
# ---------------------------------------------------------------------------


def test_get_organisation_snapshot_with_date_serialises_as_iso():
    payload = {
        "ods_code": "RGT01",
        "name": "ADDENBROOKE'S HOSPITAL",
        "trust": {"ods_code": "RGT", "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"},
    }
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_organisation_snapshot("RGT01", on_date=date(2024, 1, 15))

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/RGT01/snapshot/",
        params={"date": "2024-01-15"},
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_organisation_snapshot_without_date_omits_params():
    payload = {"ods_code": "RGT01", "name": "ADDENBROOKE'S HOSPITAL"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = get_organisation_snapshot("RGT01")

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/RGT01/snapshot/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )


def test_get_organisation_snapshot_404_raises_clear_error():
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(None, status_code=404, text="not found")
        with pytest.raises(NHSOrganisationsAPIError) as exc_info:
            get_organisation_snapshot("RGT01", on_date=date(2010, 1, 1))

    assert "No snapshot exists for organisation RGT01 on 2010-01-01" in str(
        exc_info.value
    )


def test_organisation_geography_as_of_delegates_to_snapshot():
    payload = {
        "ods_code": "RGT01",
        "name": "ADDENBROOKE'S HOSPITAL",
        "trust": {"ods_code": "RGT", "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"},
        "integrated_care_board": {"ods_code": "QUE", "name": "NHS Cambridgeshire and Peterborough ICB"},
        "nhs_england_region": {"region_code": "Y61", "name": "East of England"},
        "openuk_network": {"boundary_identifier": "EPEN", "name": "Eastern Paediatric Epilepsy Network"},
        "country": {"boundary_identifier": "E92000001", "name": "England"},
    }
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = organisation_geography_as_of("RGT01", on_date=date(2024, 1, 15))

    assert result == payload
    mock_get.assert_called_once_with(
        url=f"{API_BASE}/organisations/RGT01/snapshot/",
        params={"date": "2024-01-15"},
        timeout=DEFAULT_TIMEOUT,
    )


def test_organisation_geography_as_of_without_date_returns_current_state():
    payload = {"ods_code": "RGT01", "name": "ADDENBROOKE'S HOSPITAL"}
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(payload)
        result = organisation_geography_as_of("RGT01")

    assert result == payload


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_timeout_is_wrapped_in_api_error():
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.side_effect = Timeout("connection timed out")
        with pytest.raises(NHSOrganisationsAPIError) as exc_info:
            list_organisations()

    assert "Timed out contacting RCPCH NHS Organisations API" in str(exc_info.value)


def test_http_error_is_wrapped_in_api_error():
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse(
            None, status_code=500, text="internal server error"
        )
        with pytest.raises(NHSOrganisationsAPIError) as exc_info:
            list_organisations()

    assert "returned an error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


def test_base_url_strips_trailing_slash(settings):
    """A trailing slash on the configured base URL must not produce a
    double-slash in the request URL."""
    settings.RCPCH_NHS_ORGANISATIONS_API_URL = (
        "https://test.rcpch.ac.uk/nhs-organisations/v1/"
    )
    with patch(
        "epilepsy12.general_functions.nhs_organisations.requests.get"
    ) as mock_get:
        mock_get.return_value = _FakeResponse([])
        list_organisations()

    mock_get.assert_called_once_with(
        url="https://test.rcpch.ac.uk/nhs-organisations/v1/organisations/",
        params=None,
        timeout=DEFAULT_TIMEOUT,
    )
