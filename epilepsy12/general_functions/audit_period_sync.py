"""
Per-cohort sync: populates ``AuditPeriodOrganisation`` rows from the
``rcpch-nhs-organisations`` API snapshot endpoint.

For each ``AuditPeriod`` and each participating organisation, this module
calls the API's ``/organisations/{ods_code}/snapshot/?date={reference_date}``
endpoint and upserts an ``AuditPeriodOrganisation`` row with the hierarchy
FKs and snapshot name fields resolved from the snapshot response.

It also:
- creates any historical ``Trust`` / ``ICB`` / ``LHB`` rows returned by the
  snapshot that do not exist locally (dissolved entities, marked
  ``active=False``). Existing rows are **never updated** — the
  current-state sync (``sync_nhs_organisations``) owns the live
  name/address/etc. on these hierarchy entities, and historical names
  live in the ``*_name_snapshot`` fields on ``AuditPeriodOrganisation``;
- upserts ``OrganisationIdentity`` rows and links ``Organisation`` rows
  based on the API's succession data (``predecessor_ods_code`` in the
  snapshot response);
- records provenance on each ``AuditPeriodOrganisation`` row;
- does not overwrite already-approved rows (re-running the sync is
  idempotent and safe);
- reports missing or ambiguous hierarchy (API 404) rather than guessing.

See ``documentation/docs/development/audit-period-organisation.md`` for the
full design.
"""

from __future__ import annotations

import logging
from datetime import date as date_class
from typing import Any

from django.apps import apps
from django.db import transaction

from .nhs_organisations import (
    get_organisation,
    get_organisation_snapshot,
    NHSOrganisationsAPIError,
)
from .nhs_organisations_sync import _truncate_to_field, _parse_date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_model(name: str):
    return apps.get_model("epilepsy12", name)


def _upsert_trust(api_trust: dict[str, Any]):
    """Resolve a ``Trust`` from an API snapshot's nested trust object,
    creating it if it does not already exist locally.

    Dissolved trusts that no longer appear in the API's list endpoint are
    created here with ``active=False`` so they can serve as FK targets for
    historical memberships. Existing rows are **never updated** — the
    current-state sync (``sync_nhs_organisations``) owns the live
    name/address/etc. on ``Trust``. Historical names live in the
    ``trust_name_snapshot`` field on ``AuditPeriodOrganisation``, not by
    mutating the live ``Trust`` row.
    """
    Trust = _get_model("Trust")
    ods_code = api_trust.get("ods_code")
    if not ods_code:
        return None

    trust, created = Trust.objects.get_or_create(
        ods_code=ods_code,
        defaults={
            "name": _truncate_to_field(
                api_trust.get("name", ""), Trust, "name"
            ),
            "address_line_1": _truncate_to_field(
                api_trust.get("address_line_1") or None, Trust, "address_line_1"
            ),
            "address_line_2": _truncate_to_field(
                api_trust.get("address_line_2", ""), Trust, "address_line_2"
            ),
            "town": api_trust.get("town") or None,
            "postcode": api_trust.get("postcode") or None,
            "country": api_trust.get("country") or None,
            "telephone": api_trust.get("telephone") or None,
            "website": _truncate_to_field(
                api_trust.get("website") or None, Trust, "website"
            ),
            # A trust that only appears in a historical snapshot (not the
            # current list endpoint) is dissolved/inactive. Existing rows
            # keep whatever ``active`` value the current-state sync set.
            "active": api_trust.get("active", False),
            "published_at": _parse_date(api_trust.get("published_at")),
        },
    )
    if created:
        logger.info(
            "Created Trust %s from historical snapshot (active=%s)",
            ods_code,
            api_trust.get("active", False),
        )
    return trust


def _upsert_local_health_board(api_lhb: dict[str, Any]):
    """Resolve a ``LocalHealthBoard`` from an API snapshot's nested LHB,
    creating it if it does not already exist locally. Existing rows are never
    updated — see ``_upsert_trust`` for the rationale.
    """
    LocalHealthBoard = _get_model("LocalHealthBoard")
    ods_code = api_lhb.get("ods_code")
    if not ods_code:
        return None

    lhb, created = LocalHealthBoard.objects.get_or_create(
        ods_code=ods_code,
        defaults={
            "name": _truncate_to_field(
                api_lhb.get("name", ""), LocalHealthBoard, "name"
            ),
            "welsh_name": _truncate_to_field(
                api_lhb.get("welsh_name", ""), LocalHealthBoard, "welsh_name"
            ),
            "boundary_identifier": api_lhb.get("boundary_identifier", ""),
            "bng_e": api_lhb.get("bng_e"),
            "bng_n": api_lhb.get("bng_n"),
            "long": api_lhb.get("long"),
            "lat": api_lhb.get("lat"),
            "publication_date": _parse_date(api_lhb.get("publication_date")),
        },
    )
    if created:
        logger.info("Created LocalHealthBoard %s from historical snapshot", ods_code)
    return lhb


def _upsert_integrated_care_board(api_icb: dict[str, Any]):
    """Resolve an ``IntegratedCareBoard`` from an API snapshot's nested ICB,
    creating it if it does not already exist locally. Existing rows are never
    updated — see ``_upsert_trust`` for the rationale.
    """
    IntegratedCareBoard = _get_model("IntegratedCareBoard")
    ods_code = api_icb.get("ods_code")
    if not ods_code:
        return None

    icb, created = IntegratedCareBoard.objects.get_or_create(
        ods_code=ods_code,
        defaults={
            "name": _truncate_to_field(
                api_icb.get("name", ""), IntegratedCareBoard, "name"
            ),
            "boundary_identifier": api_icb.get("boundary_identifier", ""),
            "bng_e": api_icb.get("bng_e"),
            "bng_n": api_icb.get("bng_n"),
            "long": api_icb.get("long"),
            "lat": api_icb.get("lat"),
            "publication_date": _parse_date(api_icb.get("publication_date")),
        },
    )
    if created:
        logger.info("Created IntegratedCareBoard %s from historical snapshot", ods_code)
    return icb


def _upsert_nhs_england_region(api_region: dict[str, Any]):
    """Resolve an ``NHSEnglandRegion`` from an API snapshot's nested region,
    creating it if it does not already exist locally. Existing rows are never
    updated — see ``_upsert_trust`` for the rationale.
    """
    NHSEnglandRegion = _get_model("NHSEnglandRegion")
    region_code = api_region.get("region_code")
    if not region_code:
        return None

    region, created = NHSEnglandRegion.objects.get_or_create(
        region_code=region_code,
        defaults={
            "name": _truncate_to_field(
                api_region.get("name", ""), NHSEnglandRegion, "name"
            ),
            "boundary_identifier": api_region.get("boundary_identifier", ""),
            "bng_e": api_region.get("bng_e"),
            "bng_n": api_region.get("bng_n"),
            "long": api_region.get("long"),
            "lat": api_region.get("lat"),
            "publication_date": _parse_date(api_region.get("publication_date")),
        },
    )
    if created:
        logger.info("Created NHSEnglandRegion %s from historical snapshot", region_code)
    return region


def _upsert_country(api_country: dict[str, Any]):
    """Resolve a ``Country`` from an API snapshot's nested country object,
    creating it if it does not already exist locally. Existing rows are never
    updated — see ``_upsert_trust`` for the rationale.
    """
    Country = _get_model("Country")
    boundary_identifier = api_country.get("boundary_identifier")
    if not boundary_identifier:
        return None

    country, created = Country.objects.get_or_create(
        boundary_identifier=boundary_identifier,
        defaults={
            "name": _truncate_to_field(
                api_country.get("name", ""), Country, "name"
            ),
            "welsh_name": _truncate_to_field(
                api_country.get("welsh_name", ""), Country, "welsh_name"
            ),
            "bng_e": api_country.get("bng_e"),
            "bng_n": api_country.get("bng_n"),
            "long": api_country.get("long"),
            "lat": api_country.get("lat"),
        },
    )
    if created:
        logger.info("Created Country %s from historical snapshot", boundary_identifier)
    return country


def _upsert_openuk_network(api_network: dict[str, Any]):
    """Resolve an ``OPENUKNetwork`` from an API snapshot's nested network,
    creating it if it does not already exist locally. Existing rows are never
    updated — see ``_upsert_trust`` for the rationale.
    """
    OPENUKNetwork = _get_model("OPENUKNetwork")
    boundary_identifier = api_network.get("boundary_identifier")
    if not boundary_identifier:
        return None

    network, created = OPENUKNetwork.objects.get_or_create(
        boundary_identifier=boundary_identifier,
        defaults={
            "name": _truncate_to_field(
                api_network.get("name", ""), OPENUKNetwork, "name"
            ),
            "country": api_network.get("country", ""),
            "publication_date": _parse_date(api_network.get("publication_date")),
        },
    )
    if created:
        logger.info("Created OPENUKNetwork %s from historical snapshot", boundary_identifier)
    return network


def _resolve_or_upsert_entity(api_nested, upsert_fn, lookup_field: str):
    """Resolve a nested API entity to a local model instance, creating it
    if it doesn't already exist locally. Returns ``None`` for empty/falsy
    input. Existing rows are returned untouched — see ``_upsert_trust``
    for the rationale."""
    if not api_nested or not isinstance(api_nested, dict):
        return None
    identifier = api_nested.get(lookup_field)
    if not identifier:
        return None
    return upsert_fn(api_nested)


def _upsert_organisation_identity(
    organisation, predecessor_ods_code: str | None
):
    """Link ``organisation`` and its predecessor (if any) to a shared
    ``OrganisationIdentity``.

    If the snapshot returned a ``predecessor_ods_code``, the predecessor
    organisation is fetched or created (with ``active=False``) and both
    rows are linked to the same ``OrganisationIdentity``. If the
    organisation already has an identity, the predecessor is linked to it.
    """
    OrganisationIdentity = _get_model("OrganisationIdentity")
    Organisation = _get_model("Organisation")

    if not predecessor_ods_code:
        return None

    # Fetch or create the predecessor organisation row.
    predecessor, created = Organisation.objects.get_or_create(
        ods_code=predecessor_ods_code,
        defaults={"name": "", "active": False},
    )
    if created:
        logger.info(
            "Created predecessor Organisation %s (inactive, from succession data)",
            predecessor_ods_code,
        )

    # Resolve the shared identity.
    if organisation.identity is not None:
        identity = organisation.identity
    elif predecessor.identity is not None:
        identity = predecessor.identity
    else:
        # Neither has an identity yet — create one.
        identity = OrganisationIdentity.objects.create(
            name=organisation.name or predecessor.name or predecessor_ods_code
        )
        logger.info(
            "Created OrganisationIdentity %s for %s / %s",
            identity.pk,
            organisation.ods_code,
            predecessor_ods_code,
        )

    # Link both rows to the identity (idempotent).
    if organisation.identity_id != identity.id:
        organisation.identity = identity
        organisation.save(update_fields=["identity"])
    if predecessor.identity_id != identity.id:
        predecessor.identity = identity
        predecessor.save(update_fields=["identity"])

    return identity


# ---------------------------------------------------------------------------
# Per-organisation snapshot sync
# ---------------------------------------------------------------------------


def _fetch_snapshot_for_period(
    organisation, reference_date: date_class
) -> tuple[dict[str, Any] | None, str | None, str]:
    """Fetch the API snapshot for one organisation at the reference date.

    Returns a tuple of ``(snapshot, error, source)``:
    - ``snapshot``: the response dict, or ``None`` on error.
    - ``error``: an error message string, or ``None`` on success.
    - ``source``: ``"snapshot"`` or ``"detail_fallback"`` — which endpoint
      the snapshot came from.

    Tries the snapshot endpoint first. If it returns 404 (no temporal
    history for the date) or a response with no country (reduced shape for
    future dates), falls back to the detail endpoint, which returns the
    current state with the full hierarchy. This is the best available
    approximation for historical periods until the API backfills temporal
    history.
    """
    snapshot = None
    source = "snapshot"
    try:
        snapshot = get_organisation_snapshot(organisation.ods_code, on_date=reference_date)
        # The snapshot endpoint returns a reduced shape for future dates
        # where country is absent.
        if not snapshot.get("country"):
            snapshot = None
            source = "detail_fallback"
    except NHSOrganisationsAPIError as exc:
        error_msg = str(exc)
        if "404" not in error_msg and "No snapshot exists" not in error_msg:
            return None, error_msg, source
        # 404 — no temporal history for this date. Fall back to detail.
        source = "detail_fallback"

    if snapshot is None:
        try:
            snapshot = get_organisation(organisation.ods_code)
        except NHSOrganisationsAPIError as exc:
            return None, str(exc), source

    return snapshot, None, source


def _sync_organisation_for_period(
    organisation, audit_period, reference_date: date_class
) -> dict[str, Any]:
    """Fetch the API snapshot for one organisation at the reference date
    and upsert an ``AuditPeriodOrganisation`` row.

    Returns a dict with:
    - ``status``: "created", "updated", "skipped_approved", or "error"
    - ``error``: error message (if status == "error")
    - ``predecessor_ods_code``: if the snapshot walked the succession chain
    - ``source``: "snapshot" or "detail_fallback" — indicates whether the
      hierarchy came from the snapshot endpoint or the detail endpoint
      (fallback when the snapshot has no temporal history for the date)
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    ods_code = organisation.ods_code
    result: dict[str, Any] = {
        "status": "error",
        "error": None,
        "predecessor_ods_code": None,
        "source": "snapshot",
    }

    snapshot, error, source = _fetch_snapshot_for_period(organisation, reference_date)
    result["source"] = source
    if snapshot is None:
        result["error"] = error
        return result

    predecessor_ods_code = snapshot.get("predecessor_ods_code")
    result["predecessor_ods_code"] = predecessor_ods_code

    # Upsert dissolved hierarchy entities from the snapshot.
    trust = _resolve_or_upsert_entity(
        snapshot.get("trust"), _upsert_trust, "ods_code"
    )
    lhb = _resolve_or_upsert_entity(
        snapshot.get("local_health_board"), _upsert_local_health_board, "ods_code"
    )
    icb = _resolve_or_upsert_entity(
        snapshot.get("integrated_care_board"),
        _upsert_integrated_care_board,
        "ods_code",
    )
    region = _resolve_or_upsert_entity(
        snapshot.get("nhs_england_region"),
        _upsert_nhs_england_region,
        "region_code",
    )
    country = _resolve_or_upsert_entity(
        snapshot.get("country"), _upsert_country, "boundary_identifier"
    )
    network = _resolve_or_upsert_entity(
        snapshot.get("openuk_network"), _upsert_openuk_network, "boundary_identifier"
    )

    if country is None:
        # This should not happen with the detail-endpoint fallback, but if
        # it does, record the error rather than creating a row without a
        # country (country is a required, non-nullable FK).
        result["error"] = (
            f"No country found for {ods_code} in snapshot or detail endpoint."
        )
        return result

    # Snapshot name fields (interim display labels — see model docstring).
    trust_name = (snapshot.get("trust") or {}).get("name", "") if trust else ""
    lhb_name = (
        (snapshot.get("local_health_board") or {}).get("name", "") if lhb else ""
    )
    icb_name = (
        (snapshot.get("integrated_care_board") or {}).get("name", "") if icb else ""
    )
    region_name = (
        (snapshot.get("nhs_england_region") or {}).get("name", "") if region else ""
    )
    network_name = (
        (snapshot.get("openuk_network") or {}).get("name", "") if network else ""
    )
    country_name = (snapshot.get("country") or {}).get("name", "")

    # Link OrganisationIdentity for ODS code succession.
    _upsert_organisation_identity(organisation, predecessor_ods_code)

    defaults = {
        "included_in_reporting": True,
        "country": country,
        "trust": trust,
        "local_health_board": lhb,
        "integrated_care_board": icb,
        "nhs_england_region": region,
        "openuk_network": network,
        "trust_name_snapshot": trust_name,
        "local_health_board_name_snapshot": lhb_name,
        "integrated_care_board_name_snapshot": icb_name,
        "nhs_england_region_name_snapshot": region_name,
        "openuk_network_name_snapshot": network_name,
        "country_name_snapshot": country_name,
        "source": result["source"],
    }

    # Don't overwrite approved rows. If a row exists and is approved,
    # skip the update.
    existing = AuditPeriodOrganisation.objects.filter(
        organisation=organisation,
        audit_period=audit_period,
    ).first()

    if existing and existing.approved_at is not None:
        result["status"] = "skipped_approved"
        return result

    membership, created = AuditPeriodOrganisation.objects.update_or_create(
        organisation=organisation,
        audit_period=audit_period,
        defaults=defaults,
    )

    result["status"] = "created" if created else "updated"
    return result


# Hierarchy fields compared by the dry-run against an existing membership row.
_DRY_RUN_HIERARCHY_FIELDS = (
    ("country", "country_name_snapshot"),
    ("trust", "trust_name_snapshot"),
    ("local_health_board", "local_health_board_name_snapshot"),
    ("integrated_care_board", "integrated_care_board_name_snapshot"),
    ("nhs_england_region", "nhs_england_region_name_snapshot"),
    ("openuk_network", "openuk_network_name_snapshot"),
)


def _count_organisation_exposure(organisation, audit_period) -> dict[str, int]:
    """Count registrations and cases attached to ``organisation`` that
    the sync outcome could affect.

    Returns a dict with:
    - ``registrations_in_period``: registrations whose ``audit_period`` is
      the one being synced (the cases a membership change for this
      cohort would directly touch).
    - ``registrations_all_periods``: registrations under the organisation
      across every cohort — useful for seeing total exposure when an org
      moves trust or a trust goes inactive.
    - ``cases_all_periods``: distinct cases under the organisation across
      all cohorts. Cases without a registration are still attached to the
      organisation via ``Site``, so this counts all cases — not just
      registered ones — because a hierarchy change (trust move, trust
      going inactive) still affects which trust/LHB those cases are
      grouped under for any period they later become registered for.
    """
    Registration = _get_model("Registration")
    Site = _get_model("Site")
    Case = _get_model("Case")

    registrations_in_period = Registration.objects.filter(
        case__epilepsy12_sites__organisation=organisation,
        audit_period=audit_period,
    ).count()

    registrations_all_periods = Registration.objects.filter(
        case__epilepsy12_sites__organisation=organisation,
    ).count()

    cases_all_periods = Case.objects.filter(
        epilepsy12_sites__organisation=organisation,
    ).distinct().count()

    return {
        "registrations_in_period": registrations_in_period,
        "registrations_all_periods": registrations_all_periods,
        "cases_all_periods": cases_all_periods,
    }


def _sync_organisation_for_period_dry_run(
    organisation, audit_period, reference_date: date_class
) -> dict[str, Any]:
    """Dry-run counterpart of ``_sync_organisation_for_period``.

    Fetches the API snapshot and resolves the hierarchy entities exactly as
    the live sync would, but writes nothing to the database. Instead it
    reports what the live sync would do for this organisation and period:

    - ``status``: one of ``"create"``, ``"update"``, ``"in_sync"``,
      ``"skip_approved"``, ``"error"``.
    - ``error``: error message (only when ``status == "error"``).
    - ``source``: ``"snapshot"`` or ``"detail_fallback"``.
    - ``changes``: list of human-readable strings describing the fields
      that differ between the snapshot and the existing unapproved
      membership row (only when ``status == "update"``; empty for
      ``"in_sync"``, which means the existing row already matches the
      snapshot and the live sync would write the same values).
    - ``registration_count_in_period``: registrations whose
      ``audit_period`` is the one being synced, for cases attached to
      this organisation. The cases a membership change for this cohort
      would directly touch.
    - ``registration_count_all_periods``: registrations under the
      organisation across every cohort.
    - ``case_count_all_periods``: distinct cases under the organisation
      across all cohorts, including cases without a registration. A
      hierarchy change still affects which trust/LHB those cases are
      grouped under, so this counts all attached cases, not just
      registered ones.

    Note: this function still creates dissolved ``Trust`` / ``ICB`` / ``LHB``
    rows returned by the snapshot if they do not yet exist locally,
    because the live sync does this and the dry-run aims to reflect what
    the live sync would actually do. It does **not** create or update
    ``AuditPeriodOrganisation`` rows and does not link
    ``OrganisationIdentity`` rows. Existing hierarchy entity rows are
    never modified — the live sync only creates missing ones.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    exposure = _count_organisation_exposure(organisation, audit_period)
    result: dict[str, Any] = {
        "status": "error",
        "error": None,
        "source": "snapshot",
        "changes": [],
        "registration_count_in_period": exposure["registrations_in_period"],
        "registration_count_all_periods": exposure["registrations_all_periods"],
        "case_count_all_periods": exposure["cases_all_periods"],
    }

    snapshot, error, source = _fetch_snapshot_for_period(organisation, reference_date)
    result["source"] = source
    if snapshot is None:
        result["error"] = error
        return result

    # Upsert dissolved hierarchy entities, exactly as the live sync would.
    # This is a side effect, but it matches the live sync's behaviour and is
    # idempotent. The dry-run does not create AuditPeriodOrganisation rows.
    trust = _resolve_or_upsert_entity(
        snapshot.get("trust"), _upsert_trust, "ods_code"
    )
    lhb = _resolve_or_upsert_entity(
        snapshot.get("local_health_board"), _upsert_local_health_board, "ods_code"
    )
    icb = _resolve_or_upsert_entity(
        snapshot.get("integrated_care_board"),
        _upsert_integrated_care_board,
        "ods_code",
    )
    region = _resolve_or_upsert_entity(
        snapshot.get("nhs_england_region"),
        _upsert_nhs_england_region,
        "region_code",
    )
    country = _resolve_or_upsert_entity(
        snapshot.get("country"), _upsert_country, "boundary_identifier"
    )
    network = _resolve_or_upsert_entity(
        snapshot.get("openuk_network"), _upsert_openuk_network, "boundary_identifier"
    )

    if country is None:
        result["error"] = (
            f"No country found for {organisation.ods_code} in snapshot or "
            f"detail endpoint."
        )
        return result

    existing = AuditPeriodOrganisation.objects.filter(
        organisation=organisation,
        audit_period=audit_period,
    ).first()

    if existing and existing.approved_at is not None:
        result["status"] = "skip_approved"
        return result

    # Build the would-be snapshot names, mirroring the live sync.
    snapshot_names = {
        "country_name_snapshot": (snapshot.get("country") or {}).get("name", ""),
        "trust_name_snapshot": (
            (snapshot.get("trust") or {}).get("name", "") if trust else ""
        ),
        "local_health_board_name_snapshot": (
            (snapshot.get("local_health_board") or {}).get("name", "") if lhb else ""
        ),
        "integrated_care_board_name_snapshot": (
            (snapshot.get("integrated_care_board") or {}).get("name", "") if icb else ""
        ),
        "nhs_england_region_name_snapshot": (
            (snapshot.get("nhs_england_region") or {}).get("name", "") if region else ""
        ),
        "openuk_network_name_snapshot": (
            (snapshot.get("openuk_network") or {}).get("name", "") if network else ""
        ),
    }

    if existing is None:
        result["status"] = "create"
        return result

    # existing is unapproved — report the diff against what the live sync
    # would write. Compare FKs by PK, snapshot name fields by string, and
    # the source/included_in_reporting fields. If nothing differs, the live
    # sync would still fire update_or_create (writing the same values), but
    # there is no meaningful change to report — return "in_sync" so the
    # command can show that distinctly from a real update.
    would_be_fks = {
        "country": country,
        "trust": trust,
        "local_health_board": lhb,
        "integrated_care_board": icb,
        "nhs_england_region": region,
        "openuk_network": network,
    }
    changes: list[str] = []
    for fk_field, name_field in _DRY_RUN_HIERARCHY_FIELDS:
        existing_fk = getattr(existing, fk_field, None)
        new_fk = would_be_fks[fk_field]
        existing_pk = existing_fk.pk if existing_fk is not None else None
        new_pk = new_fk.pk if new_fk is not None else None
        if existing_pk != new_pk:
            existing_name = getattr(existing, name_field, "") or ""
            new_name = snapshot_names[name_field] or ""
            existing_label = existing_name or (
                existing_fk.ods_code if existing_fk is not None else "None"
            )
            new_label = new_name or (
                new_fk.ods_code if new_fk is not None else "None"
            )
            changes.append(f"{fk_field}: {existing_label} -> {new_label}")
        else:
            # Same FK — but the snapshot name may have changed (the live
            # sync rewrites the name from the snapshot response).
            existing_name = getattr(existing, name_field, "") or ""
            new_name = snapshot_names[name_field] or ""
            if existing_name != new_name:
                changes.append(f"{name_field}: {existing_name!r} -> {new_name!r}")

    if existing.source != source:
        changes.append(f"source: {existing.source} -> {source}")
    if existing.included_in_reporting is not True:
        # The live sync always sets included_in_reporting=True. Report it
        # only if the existing row has it set to False, since that's a
        # real change the sync would make.
        changes.append("included_in_reporting: False -> True")

    if not changes:
        result["status"] = "in_sync"
        return result

    result["status"] = "update"
    result["changes"] = changes
    return result


# ---------------------------------------------------------------------------
# Per-cohort sync
# ---------------------------------------------------------------------------


def sync_audit_period(audit_period, ods_codes=None) -> dict[str, Any]:
    """Populate ``AuditPeriodOrganisation`` rows for one audit period.

    For each organisation that has at least one registration in the audit
    period, calls the API snapshot endpoint at the period's
    ``data_collection_end_date`` and upserts a membership row.

    Args:
        ods_codes: an optional list of ODS codes to filter by. If provided,
            only organisations with these ODS codes are synced. If None,
            all organisations with registrations in the period are synced.

    Returns a dict with:
    - ``period``: the audit period's cohort number
    - ``reference_date``: the date used for snapshot calls
    - ``created``: count of newly created membership rows
    - ``updated``: count of updated membership rows
    - ``skipped_approved``: count of already-approved rows left untouched
    - ``errors``: list of (ods_code, error_message) for failed snapshots
    - ``predecessors``: list of (ods_code, predecessor_ods_code) for
      organisations whose snapshot walked the succession chain
    """
    Organisation = _get_model("Organisation")
    Registration = _get_model("Registration")

    reference_date = audit_period.data_collection_end_date

    # Organisations that have at least one registration in this period.
    participating_org_ids = (
        Registration.objects.filter(audit_period=audit_period)
        .values_list("case__epilepsy12_sites__organisation", flat=True)
        .distinct()
    )
    organisations = Organisation.objects.filter(id__in=participating_org_ids)

    # If ods_codes is provided, filter to only those organisations.
    if ods_codes:
        organisations = organisations.filter(ods_code__in=ods_codes)

    created = 0
    updated = 0
    skipped_approved = 0
    snapshot_count = 0
    detail_fallback_count = 0
    errors: list[tuple[str, str]] = []
    predecessors: list[tuple[str, str]] = []

    with transaction.atomic():
        for organisation in organisations:
            result = _sync_organisation_for_period(
                organisation, audit_period, reference_date
            )

            if result["predecessor_ods_code"]:
                predecessors.append(
                    (organisation.ods_code, result["predecessor_ods_code"])
                )

            status = result["status"]
            if status == "created":
                created += 1
                if result["source"] == "detail_fallback":
                    detail_fallback_count += 1
                else:
                    snapshot_count += 1
            elif status == "updated":
                updated += 1
                if result["source"] == "detail_fallback":
                    detail_fallback_count += 1
                else:
                    snapshot_count += 1
            elif status == "skipped_approved":
                skipped_approved += 1
            else:
                errors.append((organisation.ods_code, result["error"] or "unknown"))

    return {
        "period": audit_period.cohort_number,
        "reference_date": reference_date.isoformat(),
        "created": created,
        "updated": updated,
        "skipped_approved": skipped_approved,
        "snapshot": snapshot_count,
        "detail_fallback": detail_fallback_count,
        "errors": errors,
        "predecessors": predecessors,
    }


def sync_all_audit_periods(ods_codes=None) -> list[dict[str, Any]]:
    """Run the per-cohort sync for every audit period.

    Args:
        ods_codes: an optional list of ODS codes to filter by. If provided,
            only organisations with these ODS codes are synced in each period.

    Returns a list of per-period result dicts (see ``sync_audit_period``).
    """
    AuditPeriod = _get_model("AuditPeriod")
    results = []
    for period in AuditPeriod.objects.all().order_by("cohort_number"):
        results.append(sync_audit_period(period, ods_codes=ods_codes))
    return results


# ---------------------------------------------------------------------------
# Identity linking (post current-state sync)
# ---------------------------------------------------------------------------


def link_organisation_identities(
    reference_date: date_class | None = None,
    organisations=None,
) -> dict[str, Any]:
    """Link ``OrganisationIdentity`` rows for organisations that don't have one.

    This runs **after** ``sync_nhs_organisations`` (the current-state sync)
    has created new ``Organisation`` rows for successor ODS codes. For each
    ``Organisation`` without an ``identity`` FK, it calls the API snapshot
    endpoint at a date before the new ODS code existed. If the API walks the
    succession chain and returns a ``predecessor_ods_code``, the successor
    and predecessor are linked to the same ``OrganisationIdentity``.

    This is the step that bridges the gap when an organisation changes its
    ODS code following a trust merger or dissolution. Without it, a clinician
    employed at the new ODS code cannot access cases stored against the old
    ODS code, because the two ``Organisation`` rows are not connected.

    Args:
        reference_date: the date to use for the snapshot call. Should be a
            date before the new ODS codes existed, so the API walks the
            succession chain backwards. If ``None``, uses the earliest
            audit period's ``data_collection_end_date`` — a date by which
            all predecessor ODS codes were still in use.
        organisations: an optional queryset or iterable of ``Organisation``
            instances to process. If ``None``, processes all active
            organisations without an ``identity`` FK. Useful for testing
            or for targeting a specific subset of organisations.

    Returns a dict with:
    - ``linked``: count of organisations newly linked to an identity
    - ``already_linked``: count of organisations that already had an identity
    - ``no_predecessor``: count of organisations with no predecessor (genuinely
      new hospitals, not reorganisations)
    - "errors": list of (ods_code, error_message) for failed snapshots
    """
    Organisation = _get_model("Organisation")
    AuditPeriod = _get_model("AuditPeriod")

    if reference_date is None:
        earliest_period = (
            AuditPeriod.objects.all().order_by("cohort_number").first()
        )
        if earliest_period is None:
            return {
                "linked": 0,
                "already_linked": 0,
                "no_predecessor": 0,
                "errors": [],
            }
        reference_date = earliest_period.data_collection_end_date

    if organisations is None:
        # Organisations without an identity. We only process active
        # organisations — inactive ones are likely predecessors that have
        # already been linked by a previous run or by the per-cohort sync.
        organisations = Organisation.objects.filter(
            identity__isnull=True, active=True
        )

    linked = 0
    already_linked = 0
    no_predecessor = 0
    errors: list[tuple[str, str]] = []

    for organisation in organisations:
        if organisation.identity_id is not None:
            already_linked += 1
            continue

        try:
            snapshot = get_organisation_snapshot(
                organisation.ods_code, on_date=reference_date
            )
        except NHSOrganisationsAPIError as exc:
            errors.append((organisation.ods_code, str(exc)))
            continue

        predecessor_ods_code = snapshot.get("predecessor_ods_code")
        if not predecessor_ods_code:
            no_predecessor += 1
            continue

        identity = _upsert_organisation_identity(
            organisation, predecessor_ods_code
        )
        if identity is not None:
            linked += 1

    return {
        "linked": linked,
        "already_linked": already_linked,
        "no_predecessor": no_predecessor,
        "errors": errors,
    }