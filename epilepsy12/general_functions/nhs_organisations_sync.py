"""
Synchronises the local organisation/geography models from the
RCPCH NHS Organisations API.

The local ``Organisation``, ``Trust``, ``LocalHealthBoard``,
``IntegratedCareBoard``, ``NHSEnglandRegion``, ``OPENUKNetwork`` and
``Country`` models are a mirror of the API's current state. This module
upserts them from the API's list endpoints and wires up the foreign keys
on ``Organisation``.

The sync is idempotent: running it repeatedly produces the same result as
running it once. It does not delete rows that are absent from the API —
inactive organisations are marked ``active=False`` by the API and synced
as such, but locally-held rows are never removed by the sync (the API is
the source of truth for *state*, but this project's clinical data may
still reference organisations that the API has marked inactive).

``Country`` is synced from the dedicated ``/countries/`` endpoint with
``geom`` omitted, since the mapping component now pulls boundary tiles
from ``rcpch-census-platform`` and geometries are no longer persisted
locally. Every other entity (Trust, LHB, ICB, NHS England Region, OPEN UK
Network) is synced from its own dedicated list endpoint.

This module does not handle temporal history. For an organisation's
geography as it was on a historical date, use
:func:`epilepsy12.general_functions.nhs_organisations.organisation_geography_as_of`,
which calls the API's ``/organisations/{ods_code}/snapshot/`` endpoint.
"""

from __future__ import annotations

import logging
from datetime import date as date_class
from typing import Any

from django.apps import apps
from django.contrib.gis.geos import Point
from django.db import transaction

from .nhs_organisations import (
    list_countries,
    list_integrated_care_boards,
    list_local_health_boards,
    list_nhs_england_regions,
    list_openuk_networks,
    list_organisations,
    list_trusts,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_date(value: Any) -> date_class | None:
    """Parse an API date string into a ``date``.

    The API sometimes returns empty strings for unset dates; these become
    ``None`` rather than raising.
    """
    if not value or value == "":
        return None
    if isinstance(value, date_class):
        return value
    return date_class.fromisoformat(value)


def _parse_float(value: Any) -> float | None:
    """Parse a value into a float, returning ``None`` for empty strings."""
    if value is None or value == "":
        return None
    return float(value)


def _parse_int(value: Any) -> int | None:
    """Parse a value into an int, returning ``None`` for empty strings."""
    if value is None or value == "":
        return None
    return int(value)


def _parse_point(geocode_coordinates: Any) -> Point | None:
    """Parse the API's ``geocode_coordinates`` GeoJSON Point into a GEOS Point.

    The API returns ``{"type": "Point", "coordinates": [lon, lat]}``. The
    local ``Organisation.geocode_coordinates`` field uses SRID 27700 (BNG),
    but the API returns WGS84 coordinates. We store the point in SRID 4326
    and let the ``Organisation.save()`` signal handle any reprojection if
    needed — matching the existing behaviour where ``latitude``/``longitude``
    are stored alongside the point.
    """
    if not geocode_coordinates:
        return None
    coords = geocode_coordinates.get("coordinates")
    if not coords or len(coords) < 2:
        return None
    return Point(x=float(coords[0]), y=float(coords[1]), srid=4326)


def _get_model(name: str):
    """Lazy model lookup to avoid import-time coupling."""
    return apps.get_model("epilepsy12", name)


def _truncate_to_field(value: Any, model_class, field_name: str) -> Any:
    """Truncate a string value to the ``max_length`` of the named field.

    The ODS occasionally publishes names or addresses that exceed the local
    model's ``max_length`` constraint. Rather than letting the sync crash with
    a ``DataError`` at the DB level, this function truncates the value to fit
    and logs a warning so the issue is visible. The field widths have been
    widened (migration 0066) to reduce the likelihood of truncation, but this
    is a safety net for any field that still has a constraint.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    try:
        field = model_class._meta.get_field(field_name)
    except Exception:
        return value
    max_length = getattr(field, "max_length", None)
    if max_length and len(value) > max_length:
        logger.warning(
            "Truncating %s.%s value (%d chars) to max_length %d: %s...",
            model_class.__name__,
            field_name,
            len(value),
            max_length,
            value[:50],
        )
        return value[:max_length]
    return value


# ---------------------------------------------------------------------------
# Entity sync functions
#
# Each upserts a single entity type from its dedicated API endpoint.
# They return a dict keyed by the entity's lookup code so the organisation
# sync can resolve FKs without re-querying the database.
# ---------------------------------------------------------------------------


def sync_trusts() -> dict[str, Any]:
    """Upsert ``Trust`` rows from ``/trusts/``.

    Returns a dict mapping ``ods_code`` → ``Trust`` instance.
    """
    Trust = _get_model("Trust")
    api_trusts = list_trusts()
    trusts_by_ods_code: dict[str, Any] = {}

    for api_trust in api_trusts:
        ods_code = api_trust["ods_code"]
        defaults = {
            "name": _truncate_to_field(api_trust.get("name", ""), Trust, "name"),
            "address_line_1": _truncate_to_field(api_trust.get("address_line_1") or None, Trust, "address_line_1"),
            "address_line_2": _truncate_to_field(api_trust.get("address_line_2", ""), Trust, "address_line_2"),
            "town": api_trust.get("town") or None,
            "postcode": api_trust.get("postcode") or None,
            "country": api_trust.get("country") or None,
            "telephone": api_trust.get("telephone") or None,
            "website": _truncate_to_field(api_trust.get("website") or None, Trust, "website"),
            "active": api_trust.get("active", True),
            "published_at": _parse_date(api_trust.get("published_at")),
        }
        trust, created = Trust.objects.update_or_create(
            ods_code=ods_code, defaults=defaults
        )
        trusts_by_ods_code[ods_code] = trust
        if created:
            logger.info("Created Trust %s (%s)", ods_code, trust.name)

    logger.info("Synced %d trusts from API", len(api_trusts))
    return trusts_by_ods_code


def sync_local_health_boards() -> dict[str, Any]:
    """Upsert ``LocalHealthBoard`` rows from ``/local_health_boards/``.

    Returns a dict mapping ``ods_code`` → ``LocalHealthBoard`` instance.
    """
    LocalHealthBoard = _get_model("LocalHealthBoard")
    api_lhbs = list_local_health_boards()
    lhbs_by_ods_code: dict[str, Any] = {}

    for api_lhb in api_lhbs:
        ods_code = api_lhb["ods_code"]
        defaults = {
            "name": _truncate_to_field(api_lhb.get("name", ""), LocalHealthBoard, "name"),
            "welsh_name": _truncate_to_field(api_lhb.get("welsh_name", ""), LocalHealthBoard, "welsh_name"),
            "boundary_identifier": api_lhb.get("boundary_identifier", ""),
            "bng_e": _parse_float(api_lhb.get("bng_e")),
            "bng_n": _parse_float(api_lhb.get("bng_n")),
            "long": _parse_float(api_lhb.get("long")),
            "lat": _parse_float(api_lhb.get("lat")),
            "publication_date": _parse_date(api_lhb.get("publication_date")),
        }
        lhb, created = LocalHealthBoard.objects.update_or_create(
            ods_code=ods_code, defaults=defaults
        )
        lhbs_by_ods_code[ods_code] = lhb
        if created:
            logger.info("Created LocalHealthBoard %s (%s)", ods_code, lhb.name)

    logger.info("Synced %d local health boards from API", len(api_lhbs))
    return lhbs_by_ods_code


def sync_integrated_care_boards() -> dict[str, Any]:
    """Upsert ``IntegratedCareBoard`` rows from ``/integrated_care_boards/``.

    Returns a dict mapping ``ods_code`` → ``IntegratedCareBoard`` instance.
    """
    IntegratedCareBoard = _get_model("IntegratedCareBoard")
    api_icbs = list_integrated_care_boards()
    icbs_by_ods_code: dict[str, Any] = {}

    for api_icb in api_icbs:
        ods_code = api_icb["ods_code"]
        defaults = {
            "name": _truncate_to_field(api_icb.get("name", ""), IntegratedCareBoard, "name"),
            "boundary_identifier": api_icb.get("boundary_identifier", ""),
            "bng_e": _parse_int(api_icb.get("bng_e")),
            "bng_n": _parse_int(api_icb.get("bng_n")),
            "long": _parse_float(api_icb.get("long")),
            "lat": _parse_float(api_icb.get("lat")),
            "publication_date": _parse_date(api_icb.get("publication_date")),
        }
        icb, created = IntegratedCareBoard.objects.update_or_create(
            ods_code=ods_code, defaults=defaults
        )
        icbs_by_ods_code[ods_code] = icb
        if created:
            logger.info("Created IntegratedCareBoard %s (%s)", ods_code, icb.name)

    logger.info("Synced %d integrated care boards from API", len(api_icbs))
    return icbs_by_ods_code


def sync_nhs_england_regions() -> dict[str, Any]:
    """Upsert ``NHSEnglandRegion`` rows from ``/nhs_england_regions/``.

    Returns a dict mapping ``region_code`` → ``NHSEnglandRegion`` instance.
    """
    NHSEnglandRegion = _get_model("NHSEnglandRegion")
    api_regions = list_nhs_england_regions()
    regions_by_code: dict[str, Any] = {}

    for api_region in api_regions:
        region_code = api_region["region_code"]
        defaults = {
            "name": _truncate_to_field(api_region.get("name", ""), NHSEnglandRegion, "name"),
            "boundary_identifier": api_region.get("boundary_identifier", ""),
            "bng_e": _parse_int(api_region.get("bng_e")),
            "bng_n": _parse_int(api_region.get("bng_n")),
            "long": _parse_float(api_region.get("long")),
            "lat": _parse_float(api_region.get("lat")),
            "publication_date": _parse_date(api_region.get("publication_date")),
        }
        region, created = NHSEnglandRegion.objects.update_or_create(
            region_code=region_code, defaults=defaults
        )
        regions_by_code[region_code] = region
        if created:
            logger.info("Created NHSEnglandRegion %s (%s)", region_code, region.name)

    logger.info("Synced %d NHS England regions from API", len(api_regions))
    return regions_by_code


def sync_countries() -> dict[str, Any]:
    """Upsert ``Country`` rows from ``/countries/`` (geom omitted).

    Returns a dict mapping ``boundary_identifier`` → ``Country`` instance.

    The ``geom`` field is intentionally not set — the API omits it by default
    and the mapping component now pulls boundary tiles from
    ``rcpch-census-platform``. Existing ``geom`` values in the local DB are
    left untouched by ``update_or_create`` (they are not in ``defaults``).
    """
    Country = _get_model("Country")
    api_countries = list_countries()
    countries_by_boundary_id: dict[str, Any] = {}

    for api_country in api_countries:
        boundary_identifier = api_country["boundary_identifier"]
        defaults = {
            "name": _truncate_to_field(api_country.get("name", ""), Country, "name"),
            "welsh_name": _truncate_to_field(api_country.get("welsh_name") or None, Country, "welsh_name"),
            "bng_e": _parse_int(api_country.get("bng_e")),
            "bng_n": _parse_int(api_country.get("bng_n")),
            "long": _parse_float(api_country.get("long")),
            "lat": _parse_float(api_country.get("lat")),
            "globalid": api_country.get("globalid") or None,
        }
        country, created = Country.objects.update_or_create(
            boundary_identifier=boundary_identifier, defaults=defaults
        )
        countries_by_boundary_id[boundary_identifier] = country
        if created:
            logger.info(
                "Created Country %s (%s)", boundary_identifier, country.name
            )

    logger.info("Synced %d countries from API", len(api_countries))
    return countries_by_boundary_id


def sync_openuk_networks() -> dict[str, Any]:
    """Upsert ``OPENUKNetwork`` rows from ``/openuk_networks/``.

    Returns a dict mapping ``boundary_identifier`` → ``OPENUKNetwork`` instance.
    """
    OPENUKNetwork = _get_model("OPENUKNetwork")
    api_networks = list_openuk_networks()
    networks_by_boundary_id: dict[str, Any] = {}

    for api_network in api_networks:
        boundary_identifier = api_network["boundary_identifier"]
        defaults = {
            "name": _truncate_to_field(api_network.get("name", ""), OPENUKNetwork, "name"),
            "country": api_network.get("country", ""),
            "publication_date": _parse_date(api_network.get("publication_date")),
        }
        network, created = OPENUKNetwork.objects.update_or_create(
            boundary_identifier=boundary_identifier, defaults=defaults
        )
        networks_by_boundary_id[boundary_identifier] = network
        if created:
            logger.info(
                "Created OPENUKNetwork %s (%s)",
                boundary_identifier,
                network.name,
            )

    logger.info("Synced %d OPEN UK networks from API", len(api_networks))
    return networks_by_boundary_id


# ---------------------------------------------------------------------------
# Organisation sync
# ---------------------------------------------------------------------------


def _resolve_fk(
    nested: Any,
    lookup_map: dict[str, Any],
    key: str,
) -> Any:
    """Resolve a nested relationship object to a local model instance.

    The API returns either a dict (e.g. ``{"ods_code": "RGT", ...}``) or an
    empty string ``""`` for relationships that don't apply (e.g. a Welsh
    organisation has ``trust: ""``). Returns ``None`` for the empty-string
    case or when the key is not found in the lookup map.
    """
    if not nested or not isinstance(nested, dict):
        return None
    identifier = nested.get(key)
    if not identifier:
        return None
    return lookup_map.get(identifier)


def _lookup_by_code(model_name: str, field: str, value: str) -> Any:
    """Look up a model instance by a single field, returning ``None`` if not found."""
    if not value:
        return None
    model = _get_model(model_name)
    try:
        return model.objects.get(**{field: value})
    except model.DoesNotExist:
        logger.warning(
            "%s with %s=%s not found in local DB during organisation sync",
            model_name,
            field,
            value,
        )
        return None


def sync_organisations(
    trusts_by_ods_code: dict[str, Any] | None = None,
    lhbs_by_ods_code: dict[str, Any] | None = None,
    icbs_by_ods_code: dict[str, Any] | None = None,
    regions_by_code: dict[str, Any] | None = None,
    countries_by_boundary_id: dict[str, Any] | None = None,
    networks_by_boundary_id: dict[str, Any] | None = None,
) -> int:
    """Upsert ``Organisation`` rows from ``/organisations/``.

    The parent-entity lookup maps are optional. If any are omitted, they are
    resolved from the database by the relevant code on demand (slower but
    useful for re-syncing just organisations after a parent sync).

    Returns the number of organisations synced.
    """
    Organisation = _get_model("Organisation")
    api_organisations = list_organisations()

    count = 0
    for api_org in api_organisations:
        ods_code = api_org.get("ods_code")
        if not ods_code:
            logger.warning("Skipping organisation with no ods_code: %s", api_org)
            continue

        # Resolve FKs. If a lookup map was passed, use it; otherwise query the
        # DB by the relevant code. The empty-string case is handled by
        # _resolve_fk returning None.
        trust = _resolve_fk(
            api_org.get("trust"), trusts_by_ods_code or {}, "ods_code"
        )
        if trust is None and api_org.get("trust"):
            trust = _lookup_by_code(
                "Trust", "ods_code", api_org["trust"].get("ods_code")
            )

        lhb = _resolve_fk(
            api_org.get("local_health_board"), lhbs_by_ods_code or {}, "ods_code"
        )
        if lhb is None and api_org.get("local_health_board"):
            lhb = _lookup_by_code(
                "LocalHealthBoard",
                "ods_code",
                api_org["local_health_board"].get("ods_code"),
            )

        icb = _resolve_fk(
            api_org.get("integrated_care_board"), icbs_by_ods_code or {}, "ods_code"
        )
        if icb is None and api_org.get("integrated_care_board"):
            icb = _lookup_by_code(
                "IntegratedCareBoard",
                "ods_code",
                api_org["integrated_care_board"].get("ods_code"),
            )

        region = _resolve_fk(
            api_org.get("nhs_england_region"), regions_by_code or {}, "region_code"
        )
        if region is None and api_org.get("nhs_england_region"):
            region = _lookup_by_code(
                "NHSEnglandRegion",
                "region_code",
                api_org["nhs_england_region"].get("region_code"),
            )

        country = _resolve_fk(
            api_org.get("country"),
            countries_by_boundary_id or {},
            "boundary_identifier",
        )
        if country is None and api_org.get("country"):
            country = _lookup_by_code(
                "Country",
                "boundary_identifier",
                api_org["country"].get("boundary_identifier"),
            )

        openuk_network = _resolve_fk(
            api_org.get("openuk_network"),
            networks_by_boundary_id or {},
            "boundary_identifier",
        )
        if openuk_network is None and api_org.get("openuk_network"):
            openuk_network = _lookup_by_code(
                "OPENUKNetwork",
                "boundary_identifier",
                api_org["openuk_network"].get("boundary_identifier"),
            )

        defaults = {
            "name": _truncate_to_field(api_org.get("name") or None, Organisation, "name"),
            "website": _truncate_to_field(api_org.get("website") or None, Organisation, "website"),
            "address1": _truncate_to_field(api_org.get("address1") or None, Organisation, "address1"),
            "address2": _truncate_to_field(api_org.get("address2") or None, Organisation, "address2"),
            "address3": _truncate_to_field(api_org.get("address3") or None, Organisation, "address3"),
            "telephone": api_org.get("telephone") or None,
            "city": api_org.get("city") or None,
            "county": api_org.get("county") or None,
            "latitude": _parse_float(api_org.get("latitude")),
            "longitude": _parse_float(api_org.get("longitude")),
            "postcode": api_org.get("postcode") or None,
            "geocode_coordinates": _parse_point(api_org.get("geocode_coordinates")),
            "active": api_org.get("active", True),
            "published_at": _parse_date(api_org.get("published_at")),
            "trust": trust,
            "local_health_board": lhb,
            "integrated_care_board": icb,
            "nhs_england_region": region,
            "openuk_network": openuk_network,
            "country": country,
        }

        Organisation.objects.update_or_create(
            ods_code=ods_code, defaults=defaults
        )
        count += 1

    logger.info("Synced %d organisations from API", count)
    return count


# ---------------------------------------------------------------------------
# Top-level sync entry point
# ---------------------------------------------------------------------------


def sync_current_state() -> dict[str, int]:
    """Sync all organisation and geography models from the API.

    This is the main entry point. It syncs parent entities first (so their
    rows exist before organisations try to reference them), then syncs
    organisations with FKs wired up.

    The entire operation runs inside a single transaction so a failure
    partway through does not leave the local models in a half-synced state.

    Returns a dict with counts of each entity type synced.
    """
    with transaction.atomic():
        trusts = sync_trusts()
        lhbs = sync_local_health_boards()
        icbs = sync_integrated_care_boards()
        regions = sync_nhs_england_regions()
        countries = sync_countries()
        networks = sync_openuk_networks()

        org_count = sync_organisations(
            trusts_by_ods_code=trusts,
            lhbs_by_ods_code=lhbs,
            icbs_by_ods_code=icbs,
            regions_by_code=regions,
            countries_by_boundary_id=countries,
            networks_by_boundary_id=networks,
        )

    return {
        "trusts": len(trusts),
        "local_health_boards": len(lhbs),
        "integrated_care_boards": len(icbs),
        "nhs_england_regions": len(regions),
        "countries": len(countries),
        "openuk_networks": len(networks),
        "organisations": org_count,
    }


# ---------------------------------------------------------------------------
# Dry-run diff
#
# Compares the API's current state against the local DB and reports what
# would change if the sync were run. Does not write to the database.
# For each entity type, reports:
#   - new: in the API but not in the local DB (would be created)
#   - changed: in both, but with different field values (would be updated,
#     with the specific fields that differ)
#   - unchanged: in both, with identical field values (would be skipped)
#   - local_only: in the local DB but not in the API (would not be touched —
#     the sync never deletes)
# ---------------------------------------------------------------------------


# Field mappings: (api_field, model_field, parser)
# The parser converts the API value to the same type the DB stores, so the
# comparison is accurate. None means no conversion needed.
_TRUST_FIELDS = [
    ("name", "name", None),
    ("address_line_1", "address_line_1", None),
    ("address_line_2", "address_line_2", None),
    ("town", "town", None),
    ("postcode", "postcode", None),
    ("country", "country", None),
    ("telephone", "telephone", None),
    ("website", "website", None),
    ("active", "active", None),
    ("published_at", "published_at", _parse_date),
]

_LHB_FIELDS = [
    ("name", "name", None),
    ("welsh_name", "welsh_name", None),
    ("boundary_identifier", "boundary_identifier", None),
    ("bng_e", "bng_e", _parse_float),
    ("bng_n", "bng_n", _parse_float),
    ("long", "long", _parse_float),
    ("lat", "lat", _parse_float),
    ("publication_date", "publication_date", _parse_date),
]

_ICB_FIELDS = [
    ("name", "name", None),
    ("boundary_identifier", "boundary_identifier", None),
    ("bng_e", "bng_e", _parse_int),
    ("bng_n", "bng_n", _parse_int),
    ("long", "long", _parse_float),
    ("lat", "lat", _parse_float),
    ("publication_date", "publication_date", _parse_date),
]

_REGION_FIELDS = [
    ("name", "name", None),
    ("boundary_identifier", "boundary_identifier", None),
    ("bng_e", "bng_e", _parse_int),
    ("bng_n", "bng_n", _parse_int),
    ("long", "long", _parse_float),
    ("lat", "lat", _parse_float),
    ("publication_date", "publication_date", _parse_date),
]

_COUNTRY_FIELDS = [
    ("name", "name", None),
    ("welsh_name", "welsh_name", None),
    ("bng_e", "bng_e", _parse_int),
    ("bng_n", "bng_n", _parse_int),
    ("long", "long", _parse_float),
    ("lat", "lat", _parse_float),
    ("globalid", "globalid", None),
]

_NETWORK_FIELDS = [
    ("name", "name", None),
    ("country", "country", None),
    ("publication_date", "publication_date", _parse_date),
]

_ORG_FIELDS = [
    ("name", "name", None),
    ("website", "website", None),
    ("address1", "address1", None),
    ("address2", "address2", None),
    ("address3", "address3", None),
    ("telephone", "telephone", None),
    ("city", "city", None),
    ("county", "county", None),
    ("latitude", "latitude", _parse_float),
    ("longitude", "longitude", _parse_float),
    ("postcode", "postcode", None),
    ("active", "active", None),
    ("published_at", "published_at", _parse_date),
]


def _diff_entity(
    api_rows: list[dict[str, Any]],
    model_class,
    lookup_field: str,
    field_mappings: list[tuple],
) -> dict[str, Any]:
    """Compare API rows against local DB rows and report differences.

    Returns a dict with keys:
        new: list of (identifier, name) for rows in the API but not in the DB
        changed: list of (identifier, name, {field: (old, new)}) for rows with differences
        unchanged: count of rows with no differences
        local_only: list of (identifier, name) for rows in the DB but not in the API
    """
    new = []
    changed = []
    unchanged = 0

    api_identifiers = set()
    for api_row in api_rows:
        identifier = api_row.get(lookup_field)
        if not identifier:
            continue
        api_identifiers.add(identifier)

        # Get the local row (if it exists)
        try:
            local_obj = model_class.objects.get(**{lookup_field: identifier})
        except model_class.DoesNotExist:
            name = api_row.get("name", "")
            new.append((identifier, name))
            continue

        # Compare fields
        diffs = {}
        for api_field, model_field, parser in field_mappings:
            api_value = api_row.get(api_field)
            if parser:
                api_value = parser(api_value)
            else:
                # For string fields, match the sync's conversion behaviour:
                # if the model field allows null (null=True), the sync converts
                # empty strings to None. If the field does not allow null, the
                # sync keeps empty strings as-is. We check the model field's
                # null attribute to determine which behaviour to mirror.
                try:
                    field = model_class._meta.get_field(model_field)
                    field_allows_null = getattr(field, "null", False)
                except Exception:
                    field_allows_null = True  # safe default
                if isinstance(api_value, str) and api_value == "":
                    if field_allows_null:
                        api_value = None
                    # else: keep "" to match the sync's behaviour

            local_value = getattr(local_obj, model_field, None)

            # Compare — handle float comparison tolerance
            if isinstance(api_value, float) and isinstance(local_value, float):
                if abs(api_value - local_value) > 0.0001:
                    diffs[model_field] = (local_value, api_value)
            elif api_value != local_value:
                diffs[model_field] = (local_value, api_value)

        if diffs:
            name = api_row.get("name", "") or str(local_obj)
            changed.append((identifier, name, diffs))
        else:
            unchanged += 1

    # Find local-only rows
    local_only = []
    for local_obj in model_class.objects.all():
        identifier = getattr(local_obj, lookup_field, None)
        if identifier and identifier not in api_identifiers:
            local_only.append((identifier, str(local_obj)))

    return {
        "new": new,
        "changed": changed,
        "unchanged": unchanged,
        "local_only": local_only,
    }


def dry_run_diff(only: str | None = None) -> dict[str, dict[str, Any]]:
    """Compare the API's current state against the local DB.

    Fetches the API list endpoints and compares each entity field-by-field
    against the local DB rows. Does not write to the database.

    Returns a dict keyed by entity name, each containing the diff result
    from :func:`_diff_entity`.
    """
    results = {}

    if only is None or only == "trusts":
        Trust = _get_model("Trust")
        results["trusts"] = _diff_entity(
            list_trusts(), Trust, "ods_code", _TRUST_FIELDS
        )
    if only is None or only == "local_health_boards":
        LocalHealthBoard = _get_model("LocalHealthBoard")
        results["local_health_boards"] = _diff_entity(
            list_local_health_boards(), LocalHealthBoard, "ods_code", _LHB_FIELDS
        )
    if only is None or only == "integrated_care_boards":
        IntegratedCareBoard = _get_model("IntegratedCareBoard")
        results["integrated_care_boards"] = _diff_entity(
            list_integrated_care_boards(), IntegratedCareBoard, "ods_code", _ICB_FIELDS
        )
    if only is None or only == "nhs_england_regions":
        NHSEnglandRegion = _get_model("NHSEnglandRegion")
        results["nhs_england_regions"] = _diff_entity(
            list_nhs_england_regions(), NHSEnglandRegion, "region_code", _REGION_FIELDS
        )
    if only is None or only == "countries":
        Country = _get_model("Country")
        results["countries"] = _diff_entity(
            list_countries(), Country, "boundary_identifier", _COUNTRY_FIELDS
        )
    if only is None or only == "openuk_networks":
        OPENUKNetwork = _get_model("OPENUKNetwork")
        results["openuk_networks"] = _diff_entity(
            list_openuk_networks(), OPENUKNetwork, "boundary_identifier", _NETWORK_FIELDS
        )
    if only is None or only == "organisations":
        Organisation = _get_model("Organisation")
        results["organisations"] = _diff_entity(
            list_organisations(), Organisation, "ods_code", _ORG_FIELDS
        )

    return results
