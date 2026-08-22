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

    The API returns ``{"type": "Point", "coordinates": [lon, lat]}`` in
    WGS84 (SRID 4326). The ``Organisation.geocode_coordinates`` field is
    now SRID 4326, so no reprojection is needed.
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
            "address_line_1": _truncate_to_field(api_trust.get("address_line_1") or "", Trust, "address_line_1"),
            "address_line_2": _truncate_to_field(api_trust.get("address_line_2") or "", Trust, "address_line_2"),
            "town": api_trust.get("town") or "",
            "postcode": api_trust.get("postcode") or "",
            "country": api_trust.get("country") or "",
            "telephone": api_trust.get("telephone") or "",
            "website": _truncate_to_field(api_trust.get("website") or "", Trust, "website"),
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
            "welsh_name": _truncate_to_field(api_country.get("welsh_name") or "", Country, "welsh_name"),
            "bng_e": _parse_int(api_country.get("bng_e")),
            "bng_n": _parse_int(api_country.get("bng_n")),
            "long": _parse_float(api_country.get("long")),
            "lat": _parse_float(api_country.get("lat")),
            "globalid": api_country.get("globalid") or "",
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
            "name": _truncate_to_field(api_org.get("name") or "", Organisation, "name"),
            "website": _truncate_to_field(api_org.get("website") or "", Organisation, "website"),
            "address1": _truncate_to_field(api_org.get("address1") or "", Organisation, "address1"),
            "address2": _truncate_to_field(api_org.get("address2") or "", Organisation, "address2"),
            "address3": _truncate_to_field(api_org.get("address3") or "", Organisation, "address3"),
            "telephone": api_org.get("telephone") or "",
            "city": api_org.get("city") or "",
            "county": api_org.get("county") or "",
            "latitude": _parse_float(api_org.get("latitude")),
            "longitude": _parse_float(api_org.get("longitude")),
            "postcode": api_org.get("postcode") or "",
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
                # The sync normalises None to "" for string fields (the API
                # returns null for unset string fields, but the local DB stores
                # ""). Mirror this so the diff doesn't report spurious
                # '' → None changes.
                if api_value is None:
                    api_value = ""

            local_value = getattr(local_obj, model_field, None)
            # Also normalise None to "" for the local value, so a local None
            # compares equal to an API "".
            if local_value is None and isinstance(api_value, str):
                local_value = ""

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


# ---------------------------------------------------------------------------
# Organisation FK diff and exposure report
# ---------------------------------------------------------------------------

# Nested API relationship field → (model_field on Organisation, lookup field
# on the related model, related model name). Used to detect trust/LHB/ICB/
# region/network/country moves that the flat _ORG_FIELDS comparison misses.
_ORG_FK_FIELDS = [
    ("trust", "trust", "ods_code", "Trust"),
    ("local_health_board", "local_health_board", "ods_code", "LocalHealthBoard"),
    ("integrated_care_board", "integrated_care_board", "ods_code", "IntegratedCareBoard"),
    ("nhs_england_region", "nhs_england_region", "region_code", "NHSEnglandRegion"),
    ("openuk_network", "openuk_network", "boundary_identifier", "OPENUKNetwork"),
    ("country", "country", "boundary_identifier", "Country"),
]


def _diff_organisation_fks(
    api_org: dict[str, Any],
    local_org,
) -> dict[str, tuple]:
    """Compare the nested relationship objects in an API organisation row
    against the FKs on the local ``Organisation`` row.

    Returns a dict of ``{model_field: (old_label, new_label)}`` for FKs that
    would change. Labels are human-readable (ODS code or boundary identifier,
    plus the name where available) so the dry-run output is useful without a
    further lookup. An FK moving from a value to ``None`` (or vice versa) is
    reported, as is a move from one instance to another.

    This is separate from the flat-field ``_diff_entity`` comparison because
    the API returns nested dicts (e.g. ``{"ods_code": "RGT", ...}``) or empty
    strings for relationships that don't apply (e.g. a Welsh organisation has
    ``trust: ""``), which the flat comparison cannot handle.
    """
    diffs: dict[str, tuple] = {}
    for api_field, model_field, lookup_field, model_name in _ORG_FK_FIELDS:
        nested = api_org.get(api_field)
        # Resolve the API value to a local instance (or None).
        if not nested or not isinstance(nested, dict):
            new_instance = None
            new_label = "None"
        else:
            identifier = nested.get(lookup_field)
            if not identifier:
                new_instance = None
                new_label = "None"
            else:
                new_instance = _lookup_by_code(model_name, lookup_field, identifier)
                new_label = identifier
                name = nested.get("name")
                if name:
                    new_label = f"{identifier} ({name})"
                elif new_instance is None:
                    new_label = f"{identifier} (not in local DB)"

        existing_instance = getattr(local_org, model_field, None)
        existing_pk = existing_instance.pk if existing_instance is not None else None
        new_pk = new_instance.pk if new_instance is not None else None

        if existing_pk != new_pk:
            if existing_instance is not None:
                old_label = getattr(existing_instance, lookup_field, None) or str(existing_instance)
                old_name = getattr(existing_instance, "name", None)
                if old_name:
                    old_label = f"{old_label} ({old_name})"
            else:
                old_label = "None"
            diffs[model_field] = (old_label, new_label)

    return diffs


def _count_organisation_exposure(organisation) -> dict[str, int]:
    """Count registrations and cases attached to ``organisation`` across all
    periods, for the current-state sync's exposure report.

    Returns a dict with:
    - ``registrations_all_periods``: registrations under the organisation
      across every cohort.
    - ``registrations_in_flight``: registrations under the organisation whose
      ``audit_period`` is currently recruiting, in data collection, or in
      grace — the cohorts a current-state change could disrupt on the live
      dashboard before it is cut over to period-aware queries.
    - ``cases_all_periods``: distinct cases under the organisation across
      all cohorts, including cases without a registration (they are still
      attached via ``Site``, so a trust move or trust going inactive still
      affects which parent they group under).
    """
    Registration = _get_model("Registration")
    Case = _get_model("Case")
    AuditPeriod = _get_model("AuditPeriod")

    registrations_all_periods = Registration.objects.filter(
        case__epilepsy12_sites__organisation=organisation,
    ).count()

    # In-flight audit periods: recruiting, data collection, or grace.
    today = date_class.today()
    in_flight_period_ids = list(
        AuditPeriod.objects.filter(
            recruitment_start_date__lte=today,
            submission_deadline__gte=today,
        ).values_list("pk", flat=True)
    )
    if in_flight_period_ids:
        registrations_in_flight = Registration.objects.filter(
            case__epilepsy12_sites__organisation=organisation,
            audit_period_id__in=in_flight_period_ids,
        ).count()
    else:
        registrations_in_flight = 0

    cases_all_periods = Case.objects.filter(
        epilepsy12_sites__organisation=organisation,
    ).distinct().count()

    return {
        "registrations_all_periods": registrations_all_periods,
        "registrations_in_flight": registrations_in_flight,
        "cases_all_periods": cases_all_periods,
    }


def _count_parent_exposure(parent, parent_field: str) -> dict[str, int]:
    """Count registrations and cases under all organisations whose live
    ``Organisation.<parent_field>`` points at ``parent``.

    Used when a trust or LHB would flip ``active`` — every organisation under
    that parent is affected, so the exposure is the sum across them.
    """
    Organisation = _get_model("Organisation")
    orgs = Organisation.objects.filter(**{parent_field: parent})
    total_registrations = 0
    total_registrations_in_flight = 0
    total_cases = 0
    for org in orgs:
        exposure = _count_organisation_exposure(org)
        total_registrations += exposure["registrations_all_periods"]
        total_registrations_in_flight += exposure["registrations_in_flight"]
        total_cases += exposure["cases_all_periods"]
    return {
        "organisations": orgs.count(),
        "registrations_all_periods": total_registrations,
        "registrations_in_flight": total_registrations_in_flight,
        "cases_all_periods": total_cases,
    }


def dry_run_diff(only: str | None = None) -> dict[str, dict[str, Any]]:
    """Compare the API's current state against the local DB.

    Fetches the API list endpoints and compares each entity field-by-field
    against the local DB rows. Does not write to the database.

    Returns a dict keyed by entity name, each containing the diff result
    from :func:`_diff_entity`. For organisations, the ``changed`` entries
    are augmented with FK-move diffs (trust/LHB/ICB/region/network/country)
    that the flat-field comparison misses, and each changed organisation
    carries an ``exposure`` dict counting registrations and cases that the
    change would affect. For trusts and LHBs, entries whose ``active`` flag
    would flip carry an ``exposure`` dict counting registrations and cases
    under all organisations in that parent.
    """
    results = {}

    if only is None or only == "trusts":
        Trust = _get_model("Trust")
        results["trusts"] = _diff_entity(
            list_trusts(), Trust, "ods_code", _TRUST_FIELDS
        )
        # Attach exposure to trusts whose active flag would flip.
        for i, (identifier, name, field_diffs) in enumerate(
            results["trusts"]["changed"]
        ):
            if "active" in field_diffs:
                trust = Trust.objects.filter(ods_code=identifier).first()
                if trust is not None:
                    exposure = _count_parent_exposure(trust, "trust")
                    results["trusts"]["changed"][i] = (
                        identifier, name, field_diffs, exposure,
                    )
    if only is None or only == "local_health_boards":
        LocalHealthBoard = _get_model("LocalHealthBoard")
        results["local_health_boards"] = _diff_entity(
            list_local_health_boards(), LocalHealthBoard, "ods_code", _LHB_FIELDS
        )
        # Attach exposure to LHBs whose active flag would flip.
        for i, (identifier, name, field_diffs) in enumerate(
            results["local_health_boards"]["changed"]
        ):
            if "active" in field_diffs:
                lhb = LocalHealthBoard.objects.filter(ods_code=identifier).first()
                if lhb is not None:
                    exposure = _count_parent_exposure(lhb, "local_health_board")
                    results["local_health_boards"]["changed"][i] = (
                        identifier, name, field_diffs, exposure,
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
        api_orgs = list_organisations()
        results["organisations"] = _diff_entity(
            api_orgs, Organisation, "ods_code", _ORG_FIELDS
        )
        # Augment changed organisations with FK-move diffs and exposure.
        api_orgs_by_ods = {o.get("ods_code"): o for o in api_orgs if o.get("ods_code")}
        augmented_changed = []
        for identifier, name, field_diffs in results["organisations"]["changed"]:
            local_org = Organisation.objects.filter(ods_code=identifier).first()
            api_org = api_orgs_by_ods.get(identifier, {})
            fk_diffs = (
                _diff_organisation_fks(api_org, local_org)
                if local_org is not None
                else {}
            )
            all_diffs = {**field_diffs, **fk_diffs}
            exposure = (
                _count_organisation_exposure(local_org)
                if local_org is not None
                else {"registrations_all_periods": 0, "registrations_in_flight": 0, "cases_all_periods": 0}
            )
            augmented_changed.append(
                (identifier, name, all_diffs, exposure)
            )
        results["organisations"]["changed"] = augmented_changed

    return results


# ---------------------------------------------------------------------------
# Pre-sync safety check
# ---------------------------------------------------------------------------

# Hierarchy FK fields on Organisation whose change is high-impact (moves
# cases between reporting parents). A change to any of these triggers the
# safety check.
_HIGH_IMPACT_ORG_FK_FIELDS = {
    "trust",
    "local_health_board",
    "integrated_care_board",
    "nhs_england_region",
    "openuk_network",
    "country",
}


def pre_sync_safety_check(only: str | None = None) -> dict[str, Any]:
    """Run the dry-run diff and decide whether the live sync is safe.

    This is the guard that runs before the live ``sync_current_state``
    commits. It enforces two rules:

    1. **Ordering constraint** — if the sync would move any organisation's
       trust/LHB (or flip any trust/LHB ``active``), and any in-flight audit
       period (recruiting / data collection / grace) has no approved
       ``AuditPeriodOrganisation`` rows, the sync is blocked. Historical
       memberships must be frozen *before* the live rows are mutated,
       otherwise the live dashboard has no period-aware source of truth to
       fall back to and cases would be silently reattributed.

    2. **Impact confirmation** — if the sync would affect any registrations
       or cases (an organisation moving trust/LHB, or a trust/LHB going
       inactive), the caller must confirm explicitly. The exposure counts are
       returned so the command can print them and require ``--confirm``.

    Returns a dict with:
    - ``blocked``: bool — True if the ordering constraint blocks the sync.
    - ``block_reason``: str — human-readable explanation if blocked.
    - ``requires_confirm``: bool — True if the sync would affect
      registrations/cases and the caller must confirm.
    - ``total_registrations``: int — registrations across all changed entities.
    - ``total_registrations_in_flight``: int — in-flight registrations affected.
    - ``total_cases``: int — distinct cases affected.
    - ``high_impact_changes``: list of (entity, identifier, description) for
      the changes that triggered the impact confirmation.
    """
    diffs = dry_run_diff(only=only)

    total_registrations = 0
    total_registrations_in_flight = 0
    total_cases = 0
    high_impact_changes: list[tuple[str, str, str]] = []
    has_org_fk_move = False
    has_parent_active_flip = False

    for entity_name, diff in diffs.items():
        for entry in diff.get("changed", []):
            identifier = entry[0]
            field_diffs = entry[2]
            exposure = entry[3] if len(entry) > 3 else None

            # Detect organisation FK moves.
            if entity_name == "organisations":
                moved_fks = _HIGH_IMPACT_ORG_FK_FIELDS & set(field_diffs.keys())
                if moved_fks:
                    has_org_fk_move = True
                    for fk in sorted(moved_fks):
                        old_label, new_label = field_diffs[fk]
                        high_impact_changes.append(
                            (entity_name, identifier, f"{fk}: {old_label} -> {new_label}")
                        )

            # Detect trust/LHB active flips.
            if entity_name in ("trusts", "local_health_boards") and "active" in field_diffs:
                has_parent_active_flip = True
                old_active, new_active = field_diffs["active"]
                high_impact_changes.append(
                    (entity_name, identifier, f"active: {old_active} -> {new_active}")
                )

            if exposure:
                total_registrations += exposure.get("registrations_all_periods", 0)
                total_registrations_in_flight += exposure.get("registrations_in_flight", 0)
                total_cases += exposure.get("cases_all_periods", 0)

    requires_confirm = bool(total_registrations or total_cases)

    # Ordering constraint: if the sync would move orgs or flip parent active,
    # and any in-flight period lacks approved memberships, block.
    blocked = False
    block_reason = ""
    if (has_org_fk_move or has_parent_active_flip) and only in (None, "organisations", "trusts", "local_health_boards"):
        AuditPeriod = _get_model("AuditPeriod")
        AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
        today = date_class.today()
        in_flight_periods = AuditPeriod.objects.filter(
            recruitment_start_date__lte=today,
            submission_deadline__gte=today,
        )
        unapproved_in_flight = []
        for period in in_flight_periods:
            approved_count = AuditPeriodOrganisation.objects.filter(
                audit_period=period,
                approved_at__isnull=False,
            ).count()
            if approved_count == 0:
                unapproved_in_flight.append(period.cohort_number)
        if unapproved_in_flight:
            blocked = True
            block_reason = (
                "This sync would move organisations between trusts/LHBs or flip "
                "a trust/LHB active flag, but the following in-flight audit "
                f"periods have no approved AuditPeriodOrganisation rows: "
                f"{', '.join(str(c) for c in unapproved_in_flight)}. Run "
                "`sync_audit_period_organisations` first to freeze historical "
                "memberships before mutating live organisation rows."
            )

    return {
        "blocked": blocked,
        "block_reason": block_reason,
        "requires_confirm": requires_confirm,
        "total_registrations": total_registrations,
        "total_registrations_in_flight": total_registrations_in_flight,
        "total_cases": total_cases,
        "high_impact_changes": high_impact_changes,
    }
