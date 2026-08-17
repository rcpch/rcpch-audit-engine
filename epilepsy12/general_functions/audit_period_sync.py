"""
Per-cohort sync: populates ``AuditPeriodOrganisation`` rows from the
``rcpch-nhs-organisations`` API snapshot endpoint.

For each ``AuditPeriod`` and each participating organisation, this module
calls the API's ``/organisations/{ods_code}/snapshot/?date={reference_date}``
endpoint and upserts an ``AuditPeriodOrganisation`` row with the hierarchy
FKs and snapshot name fields resolved from the snapshot response.

It also:
- upserts any historical ``Trust`` / ``ICB`` / ``LHB`` rows returned by the
  snapshot that do not exist locally (dissolved entities, marked
  ``active=False``);
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

from .nhs_organisations import get_organisation_snapshot, NHSOrganisationsAPIError
from .nhs_organisations_sync import _truncate_to_field, _parse_date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_model(name: str):
    return apps.get_model("epilepsy12", name)


def _upsert_trust(api_trust: dict[str, Any]):
    """Upsert a ``Trust`` row from an API snapshot's nested trust object.

    Dissolved trusts that no longer appear in the API's list endpoint are
    upserted here with ``active=False`` so they can serve as FK targets for
    historical memberships.
    """
    Trust = _get_model("Trust")
    ods_code = api_trust.get("ods_code")
    if not ods_code:
        return None

    defaults = {
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
        "active": api_trust.get("active", False),
        "published_at": _parse_date(api_trust.get("published_at")),
    }
    trust, _ = Trust.objects.update_or_create(
        ods_code=ods_code, defaults=defaults
    )
    return trust


def _upsert_local_health_board(api_lhb: dict[str, Any]):
    """Upsert a ``LocalHealthBoard`` row from an API snapshot's nested LHB."""
    LocalHealthBoard = _get_model("LocalHealthBoard")
    ods_code = api_lhb.get("ods_code")
    if not ods_code:
        return None

    defaults = {
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
    }
    lhb, _ = LocalHealthBoard.objects.update_or_create(
        ods_code=ods_code, defaults=defaults
    )
    return lhb


def _upsert_integrated_care_board(api_icb: dict[str, Any]):
    """Upsert an ``IntegratedCareBoard`` row from an API snapshot's nested ICB."""
    IntegratedCareBoard = _get_model("IntegratedCareBoard")
    ods_code = api_icb.get("ods_code")
    if not ods_code:
        return None

    defaults = {
        "name": _truncate_to_field(
            api_icb.get("name", ""), IntegratedCareBoard, "name"
        ),
        "boundary_identifier": api_icb.get("boundary_identifier", ""),
        "bng_e": api_icb.get("bng_e"),
        "bng_n": api_icb.get("bng_n"),
        "long": api_icb.get("long"),
        "lat": api_icb.get("lat"),
        "publication_date": _parse_date(api_icb.get("publication_date")),
    }
    icb, _ = IntegratedCareBoard.objects.update_or_create(
        ods_code=ods_code, defaults=defaults
    )
    return icb


def _upsert_nhs_england_region(api_region: dict[str, Any]):
    """Upsert an ``NHSEnglandRegion`` row from an API snapshot's nested region."""
    NHSEnglandRegion = _get_model("NHSEnglandRegion")
    region_code = api_region.get("region_code")
    if not region_code:
        return None

    defaults = {
        "name": _truncate_to_field(
            api_region.get("name", ""), NHSEnglandRegion, "name"
        ),
        "boundary_identifier": api_region.get("boundary_identifier", ""),
        "bng_e": api_region.get("bng_e"),
        "bng_n": api_region.get("bng_n"),
        "long": api_region.get("long"),
        "lat": api_region.get("lat"),
        "publication_date": _parse_date(api_region.get("publication_date")),
    }
    region, _ = NHSEnglandRegion.objects.update_or_create(
        region_code=region_code, defaults=defaults
    )
    return region


def _upsert_country(api_country: dict[str, Any]):
    """Upsert a ``Country`` row from an API snapshot's nested country object."""
    Country = _get_model("Country")
    boundary_identifier = api_country.get("boundary_identifier")
    if not boundary_identifier:
        return None

    defaults = {
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
    }
    country, _ = Country.objects.update_or_create(
        boundary_identifier=boundary_identifier, defaults=defaults
    )
    return country


def _upsert_openuk_network(api_network: dict[str, Any]):
    """Upsert an ``OPENUKNetwork`` row from an API snapshot's nested network."""
    OPENUKNetwork = _get_model("OPENUKNetwork")
    boundary_identifier = api_network.get("boundary_identifier")
    if not boundary_identifier:
        return None

    defaults = {
        "name": _truncate_to_field(
            api_network.get("name", ""), OPENUKNetwork, "name"
        ),
        "country": api_network.get("country", ""),
        "publication_date": _parse_date(api_network.get("publication_date")),
    }
    network, _ = OPENUKNetwork.objects.update_or_create(
        boundary_identifier=boundary_identifier, defaults=defaults
    )
    return network


def _resolve_or_upsert_entity(api_nested, upsert_fn, lookup_field: str):
    """Resolve a nested API entity to a local model instance, upserting it
    if it doesn't already exist. Returns ``None`` for empty/falsy input."""
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


def _sync_organisation_for_period(
    organisation, audit_period, reference_date: date_class
) -> dict[str, Any]:
    """Fetch the API snapshot for one organisation at the reference date
    and upsert an ``AuditPeriodOrganisation`` row.

    Returns a dict with:
    - ``status``: "created", "updated", "skipped_approved", or "error"
    - ``error``: error message (if status == "error")
    - ``predecessor_ods_code``: if the snapshot walked the succession chain
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    ods_code = organisation.ods_code
    result: dict[str, Any] = {
        "status": "error",
        "error": None,
        "predecessor_ods_code": None,
    }

    try:
        snapshot = get_organisation_snapshot(ods_code, on_date=reference_date)
    except NHSOrganisationsAPIError as exc:
        result["error"] = str(exc)
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
        result["error"] = (
            f"Snapshot for {ods_code} at {reference_date} returned no country."
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
        "source": "api_snapshot",
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


# ---------------------------------------------------------------------------
# Per-cohort sync
# ---------------------------------------------------------------------------


def sync_audit_period(audit_period) -> dict[str, Any]:
    """Populate ``AuditPeriodOrganisation`` rows for one audit period.

    For each organisation that has at least one registration in the audit
    period, calls the API snapshot endpoint at the period's
    ``data_collection_end_date`` and upserts a membership row.

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

    created = 0
    updated = 0
    skipped_approved = 0
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
            elif status == "updated":
                updated += 1
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
        "errors": errors,
        "predecessors": predecessors,
    }


def sync_all_audit_periods() -> list[dict[str, Any]]:
    """Run the per-cohort sync for every audit period.

    Returns a list of per-period result dicts (see ``sync_audit_period``).
    """
    AuditPeriod = _get_model("AuditPeriod")
    results = []
    for period in AuditPeriod.objects.all().order_by("cohort_number"):
        results.append(sync_audit_period(period))
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