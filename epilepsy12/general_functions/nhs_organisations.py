"""
Low-level client for the RCPCH NHS Organisations API.

This service is the source of truth for organisations, trusts, local health
boards, integrated care boards, NHS England regions, OPEN UK networks, country
and their history (including mergers and ODS code successions). The local
``Organisation`` / ``Trust`` / etc. models in this project are a synchronised
mirror of this API; the :func:`organisation_geography_as_of` function below is
the only live API call used outside the sync path — it is called by the public
KPI publication flow to resolve an organisation's geography as it was on a
given date.

Not every entity has its own list endpoint. The API exposes dedicated list
endpoints for organisations, trusts, local health boards, integrated care
boards, NHS England regions, countries and OPEN UK networks.

The ``/countries/`` endpoint returns the full ``geom`` MultiPolygon by
default, which is large. Since the mapping component now pulls boundary
tiles from ``rcpch-census-platform`` and this project no longer needs to
persist geometries locally, the country client functions omit ``geom`` by
default via the API's ``fields`` parameter.

The API is unauthenticated for read endpoints. The base URL defaults to the
public ``https://api.rcpch.ac.uk/nhs-organisations/v1`` endpoint and can be
overridden via the ``RCPCH_NHS_ORGANISATIONS_API_URL`` setting.

Endpoint reference: https://rcpch-nhs-organisations.azurewebsites.net/schema/
"""

import logging
from datetime import date as date_class
from typing import Any
from urllib.parse import urlencode

import requests
from django.conf import settings
from requests.exceptions import HTTPError, Timeout

logger = logging.getLogger(__name__)

# Default request timeout in seconds.
DEFAULT_TIMEOUT = 10


class NHSOrganisationsAPIError(Exception):
    """Raised when the RCPCH NHS Organisations API returns an unrecoverable error."""


def _base_url() -> str:
    """Return the configured API base URL, with no trailing slash."""
    return settings.RCPCH_NHS_ORGANISATIONS_API_URL.rstrip("/")


def _request(path: str, params: dict[str, Any] | None = None) -> Any:
    """Perform a GET against the API and return parsed JSON.

    Raises :class:`NHSOrganisationsAPIError` on network or HTTP errors so
    callers do not have to catch ``requests`` exceptions directly.
    """
    url = f"{_base_url()}{path}"
    try:
        response = requests.get(
            url=url,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except Timeout as exc:
        raise NHSOrganisationsAPIError(
            f"Timed out contacting RCPCH NHS Organisations API at {url}"
        ) from exc
    except HTTPError as exc:
        raise NHSOrganisationsAPIError(
            f"RCPCH NHS Organisations API returned an error for {url}: "
            f"{exc.response.status_code} {exc.response.text}"
        ) from exc

    return response.json()


# ---------------------------------------------------------------------------
# Current-state list endpoints
#
# These return the API's current-state rows. Each list endpoint accepts
# optional filter parameters (e.g. ``ods_code``, ``active``); when no filters
# are passed, the full list is returned. The /organisations/ endpoint nests
# every relationship (trust, local_health_board, integrated_care_board,
# nhs_england_region, openuk_network, country, paediatric_diabetes_unit,
# local_authority_district, lower_layer_super_output_area, london_borough)
# inline, so a single pass through it is enough to populate both the entity
# rows and the foreign keys on the local Organisation model.
# ---------------------------------------------------------------------------


def list_organisations(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of organisations with all nested relationships.

    Accepts the filter parameters documented by the API (``ods_code``,
    ``active``, ``name``, ``postcode``, etc.). With no filters, returns every
    organisation.

    Each organisation in the response nests its ``trust``, ``local_health_board``,
    ``integrated_care_board``, ``nhs_england_region``, ``openuk_network``,
    ``country``, ``paediatric_diabetes_unit``, ``local_authority_district``,
    ``lower_layer_super_output_area`` and ``london_borough`` inline. The sync
    path uses this single endpoint to populate every foreign key on
    ``Organisation`` in one pass. The parent entity tables themselves
    (``Trust``, ``OPENUKNetwork``, ``Country``, etc.) are synced from their
    dedicated list endpoints.
    """
    return _request("/organisations/", params=filters or None)


def list_trusts(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of NHS Trusts (England). Accepts ``ods_code``, ``active``,
    ``name``, etc."""
    return _request("/trusts/", params=filters or None)


def list_local_health_boards(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of Local Health Boards (Wales). Accepts ``ods_code``,
    ``name``, etc."""
    return _request("/local_health_boards/", params=filters or None)


def list_integrated_care_boards(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of Integrated Care Boards (England). Accepts ``ods_code``,
    ``name``, etc."""
    return _request("/integrated_care_boards/", params=filters or None)


def list_nhs_england_regions(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of NHS England regions. Accepts ``region_code``, ``name``,
    etc."""
    return _request("/nhs_england_regions/", params=filters or None)


def list_countries(
    *, include_geom: bool = False, **filters: Any
) -> list[dict[str, Any]]:
    """Return a list of countries.

    The API returns the full ``geom`` MultiPolygon by default, which is large.
    Since the mapping component now pulls boundary tiles from
    ``rcpch-census-platform`` and this project no longer needs to persist
    geometries locally, ``geom`` is omitted by default. Pass
    ``include_geom=True`` to request it.

    Accepts the filter parameters documented by the API
    (``boundary_identifier``, ``name``, ``welsh_name``, etc.).
    """
    params: dict[str, Any] = dict(filters)
    if not include_geom:
        # Omit the heavy geometry column. The API supports a comma-separated
        # ``fields`` parameter; listing every field except ``geom`` keeps the
        # response shape stable if the API adds new non-geometry fields later.
        params["fields"] = (
            "boundary_identifier,name,welsh_name,bng_e,bng_n,long,lat,globalid"
        )
    return _request("/countries/", params=params or None)


def list_openuk_networks(**filters: Any) -> list[dict[str, Any]]:
    """Return a list of OPEN UK Networks (paediatric epilepsy networks).

    Accepts the filter parameters documented by the API
    (``boundary_identifier``, ``name``, ``country``, ``publication_date``).
    With no filters, returns every network.
    """
    return _request("/openuk_networks/", params=filters or None)


# ---------------------------------------------------------------------------
# Single-resource retrieve endpoints
# ---------------------------------------------------------------------------


def get_organisation(ods_code: str) -> dict[str, Any]:
    """Return a single organisation with all nested relationships, by ODS code."""
    return _request(f"/organisations/{ods_code}/")


def get_trust(ods_code: str) -> dict[str, Any]:
    """Return a single NHS Trust by ODS code."""
    return _request(f"/trusts/{ods_code}/")


def get_local_health_board(ods_code: str) -> dict[str, Any]:
    """Return a single Local Health Board by ODS code."""
    return _request(f"/local_health_boards/{ods_code}/")


def get_integrated_care_board(ods_code: str) -> dict[str, Any]:
    """Return a single Integrated Care Board by ODS code."""
    return _request(f"/integrated_care_boards/{ods_code}/")


def get_nhs_england_region(region_code: str) -> dict[str, Any]:
    """Return a single NHS England region by region code."""
    return _request(f"/nhs_england_regions/{region_code}/")


def get_country(
    boundary_identifier: str, *, include_geom: bool = False
) -> dict[str, Any]:
    """Return a single country by boundary identifier (e.g. ``E92000001``).

    The API returns the full ``geom`` MultiPolygon by default, which is large.
    Since the mapping component now pulls boundary tiles from
    ``rcpch-census-platform`` and this project no longer needs to persist
    geometries locally, ``geom`` is omitted by default. Pass
    ``include_geom=True`` to request it.
    """
    params: dict[str, Any] | None = None
    if not include_geom:
        params = {
            "fields": (
                "boundary_identifier,name,welsh_name,bng_e,bng_n,long,lat,globalid"
            )
        }
    return _request(
        f"/countries/{boundary_identifier}/", params=params
    )


def get_openuk_network(boundary_identifier: str) -> dict[str, Any]:
    """Return a single OPEN UK Network by boundary identifier
    (e.g. ``EPEN`` for the Eastern Paediatric Epilepsy Network)."""
    return _request(f"/openuk_networks/{boundary_identifier}/")


# ---------------------------------------------------------------------------
# Temporal snapshot endpoint
#
# This is the as_of primitive. It returns the full geography of an organisation
# as it was on a given date. If the organisation did not yet exist on that date
# (for example because its ODS code was introduced by a merger), the endpoint
# walks the OrganisationSuccession chain to the predecessor and returns the
# predecessor's state, with ``predecessor_ods_code`` populated.
#
# Returns 404 if no state exists for the date (e.g. before the API's
# installation day, or for an unknown ODS code).
# ---------------------------------------------------------------------------


def get_organisation_snapshot(
    ods_code: str, on_date: date_class | None = None
) -> dict[str, Any]:
    """Return an organisation's geography as it was on ``on_date``.

    If ``on_date`` is ``None``, returns the current state.

    Raises :class:`NHSOrganisationsAPIError` if the API returns a 404 (no state
    exists for the date) or any other error.
    """
    params: dict[str, Any] | None = None
    if on_date is not None:
        params = {"date": on_date.isoformat()}
    try:
        return _request(f"/organisations/{ods_code}/snapshot/", params=params)
    except NHSOrganisationsAPIError as exc:
        # Re-raise with a clearer message for the 404 case; callers (the
        # publication flow) need to distinguish "no history for this date"
        # from a generic API failure.
        if "404" in str(exc):
            raise NHSOrganisationsAPIError(
                f"No snapshot exists for organisation {ods_code} on "
                f"{on_date.isoformat() if on_date else 'today'}. "
                "The organisation may not have existed on that date, or the "
                "date is before the API's temporal history installation day."
            ) from exc
        raise


def organisation_geography_as_of(
    ods_code: str, on_date: date_class | None = None
) -> dict[str, Any]:
    """Return an organisation's full geography as it was on ``on_date``.

    This is the function the public KPI publication flow imports. It is a thin
    wrapper around :func:`get_organisation_snapshot` and is the only live API
    call used outside the sync path. It does not touch the local models.

    The returned dict has the shape documented in the API schema: the
    organisation's own attributes (``name``, ``address1``, ``postcode``, etc.)
    plus nested ``trust`` / ``local_health_board`` / ``integrated_care_board``
    / ``nhs_england_region`` / ``openuk_network`` / ``country`` /
    ``paediatric_diabetes_unit`` objects as they were on the given date. If a
    predecessor was walked to, ``predecessor_ods_code`` is populated.
    """
    return get_organisation_snapshot(ods_code, on_date=on_date)
