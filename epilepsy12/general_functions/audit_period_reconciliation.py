"""
Post-sync reconciliation: confirms that the per-cohort sync correctly
applied hierarchy changes and that the attribution chain is intact.

This module produces a verification report that the audit team can review
after running ``sync_audit_period_organisations``. It is the counterpart to
the sync command's ``--dry-run`` flag: the dry-run signposts the changes
expected, and this module confirms that the sync was successful.

For a given audit period, the reconciliation report includes:

1. **Hierarchy changes** — for each organisation that has a membership row
   in both this period and the previous period, reports whether the parent
   (Trust/LHB) changed. This confirms that mergers/acquisitions/reorganisations
   flowed through the sync correctly.

2. **Registration attribution** — for each organisation and audit period,
   counts the registrations attributed to it via
   ``Registration.audit_period`` → ``AuditPeriodOrganisation``. This
   confirms that the attribution chain is intact and that registrations
   are not orphaned.

3. **Sibling organisations** — for each organisation and audit period,
   lists the sibling organisations under the same Trust/LHB. This confirms
   that after a merger/affiliation/split, an organisation correctly has the
   right siblings.

See ``documentation/docs/development/audit-period-organisation.md`` for the
full design.
"""

from __future__ import annotations

import logging
from typing import Any

from django.apps import apps
from django.db.models import Count

logger = logging.getLogger(__name__)


def _get_model(name: str):
    return apps.get_model("epilepsy12", name)


def _get_previous_period(audit_period):
    """Return the audit period immediately before the given one, or None."""
    AuditPeriod = _get_model("AuditPeriod")
    return (
        AuditPeriod.objects.filter(
            cohort_number__lt=audit_period.cohort_number
        )
        .order_by("-cohort_number")
        .first()
    )


def reconcile_hierarchy_changes(audit_period) -> list[dict[str, Any]]:
    """Report hierarchy changes between the previous period and this one.

    For each organisation that has an approved membership in both periods,
    reports whether its Trust or LHB changed. This confirms that
    mergers/acquisitions/reorganisations flowed through the sync correctly.

    Returns a list of dicts, one per organisation with a change:
    - ``organisation_id``: int
    - ``ods_code``: str
    - ``organisation_name``: str
    - ``previous_trust``: str | None (trust name or None)
    - ``current_trust``: str | None
    - ``previous_lhb``: str | None
    - ``current_lhb``: str | None
    - ``changed``: bool — True if trust or LHB changed
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    previous_period = _get_previous_period(audit_period)
    if previous_period is None:
        return []

    current_memberships = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=False,
    ).select_related("organisation", "trust", "local_health_board")

    changes: list[dict[str, Any]] = []

    for current in current_memberships:
        try:
            previous = AuditPeriodOrganisation.objects.select_related(
                "trust", "local_health_board"
            ).get(
                organisation=current.organisation,
                audit_period=previous_period,
                approved_at__isnull=False,
            )
        except AuditPeriodOrganisation.DoesNotExist:
            continue

        prev_trust = previous.trust.name if previous.trust else None
        curr_trust = current.trust.name if current.trust else None
        prev_lhb = (
            previous.local_health_board.name
            if previous.local_health_board
            else None
        )
        curr_lhb = (
            current.local_health_board.name
            if current.local_health_board
            else None
        )

        if prev_trust != curr_trust or prev_lhb != curr_lhb:
            changes.append(
                {
                    "organisation_id": current.organisation_id,
                    "ods_code": current.organisation.ods_code,
                    "organisation_name": current.organisation.name,
                    "previous_trust": prev_trust,
                    "current_trust": curr_trust,
                    "previous_lhb": prev_lhb,
                    "current_lhb": curr_lhb,
                    "changed": True,
                }
            )

    return changes


def reconcile_registration_attribution(audit_period) -> dict[str, Any]:
    """Confirm that registrations are correctly attributed to organisations
    via the period-aware hierarchy.

    For each organisation with a membership row in the period, counts the
    registrations attributed to it. Reports any organisations that have
    registrations but no membership row (orphaned registrations), and any
    membership rows with no registrations (orphaned memberships).

    Returns a dict with:
    - ``period``: cohort number
    - ``organisation_counts``: list of dicts with ``ods_code``, ``name``,
      ``registration_count``, ``membership_status`` ("approved",
      "unapproved", or "missing")
    - ``orphaned_registrations``: list of organisation IDs that have
      registrations in the period but no membership row
    - ``orphaned_memberships``: list of organisation IDs that have a
      membership row but no registrations in the period
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
    Registration = _get_model("Registration")
    Organisation = _get_model("Organisation")

    # Count registrations per organisation for this period.
    reg_counts = dict(
        Registration.objects.filter(audit_period=audit_period)
        .values("case__epilepsy12_sites__organisation")
        .annotate(count=Count("id", distinct=True))
        .values_list("case__epilepsy12_sites__organisation", "count")
    )

    memberships = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period
    ).select_related("organisation")

    org_counts: list[dict[str, Any]] = []
    membership_org_ids = set()

    for m in memberships:
        membership_org_ids.add(m.organisation_id)
        reg_count = reg_counts.get(m.organisation_id, 0)
        status = "approved" if m.approved_at is not None else "unapproved"
        org_counts.append(
            {
                "ods_code": m.organisation.ods_code,
                "name": m.organisation.name,
                "registration_count": reg_count,
                "membership_status": status,
            }
        )

    # Organisations with registrations but no membership row.
    reg_org_ids = set(reg_counts.keys())
    orphaned_reg_ids = reg_org_ids - membership_org_ids

    orphaned_registrations: list[dict[str, Any]] = []
    for org_id in orphaned_reg_ids:
        try:
            org = Organisation.objects.get(pk=org_id)
            orphaned_registrations.append(
                {
                    "organisation_id": org_id,
                    "ods_code": org.ods_code,
                    "name": org.name,
                    "registration_count": reg_counts[org_id],
                }
            )
        except Organisation.DoesNotExist:
            orphaned_registrations.append(
                {
                    "organisation_id": org_id,
                    "ods_code": "?",
                    "name": f"Organisation {org_id} not found",
                    "registration_count": reg_counts[org_id],
                }
            )

    # Membership rows with no registrations.
    orphaned_membership_ids = membership_org_ids - reg_org_ids
    orphaned_memberships: list[dict[str, Any]] = []
    for m in memberships:
        if m.organisation_id in orphaned_membership_ids:
            orphaned_memberships.append(
                {
                    "organisation_id": m.organisation_id,
                    "ods_code": m.organisation.ods_code,
                    "name": m.organisation.name,
                }
            )

    return {
        "period": audit_period.cohort_number,
        "organisation_counts": org_counts,
        "orphaned_registrations": orphaned_registrations,
        "orphaned_memberships": orphaned_memberships,
    }


def reconcile_sibling_organisations(audit_period) -> list[dict[str, Any]]:
    """Confirm that each organisation has the correct sibling organisations
    for the audit period.

    For each organisation with an approved membership, lists the sibling
    organisations under the same Trust or LHB. This confirms that after a
    merger/affiliation/split, an organisation correctly has the right
    siblings.

    Returns a list of dicts, one per organisation with an approved
    membership:
    - ``ods_code``: str
    - ``organisation_name``: str
    - ``parent_type``: "trust" or "local_health_board" or None
    - ``parent_name``: str | None
    - ``sibling_count``: int
    - ``siblings``: list of dicts with ``ods_code`` and ``name``
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    memberships = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=False,
        included_in_reporting=True,
    ).select_related("organisation", "trust", "local_health_board")

    results: list[dict[str, Any]] = []

    for membership in memberships:
        if membership.trust is not None:
            parent_field = "trust"
            parent = membership.trust
        elif membership.local_health_board is not None:
            parent_field = "local_health_board"
            parent = membership.local_health_board
        else:
            results.append(
                {
                    "ods_code": membership.organisation.ods_code,
                    "organisation_name": membership.organisation.name,
                    "parent_type": None,
                    "parent_name": None,
                    "sibling_count": 0,
                    "siblings": [],
                }
            )
            continue

        siblings = (
            AuditPeriodOrganisation.objects.filter(
                **{
                    parent_field: parent,
                    "audit_period": audit_period,
                    "approved_at__isnull": False,
                    "included_in_reporting": True,
                }
            ).exclude(organisation_id=membership.organisation_id)
            .select_related("organisation")
        )

        sibling_list = [
            {"ods_code": s.organisation.ods_code, "name": s.organisation.name}
            for s in siblings
        ]

        results.append(
            {
                "ods_code": membership.organisation.ods_code,
                "organisation_name": membership.organisation.name,
                "parent_type": parent_field,
                "parent_name": parent.name,
                "sibling_count": len(sibling_list),
                "siblings": sibling_list,
            }
        )

    return results


def reconcile_period(audit_period) -> dict[str, Any]:
    """Produce a full reconciliation report for the given audit period.

    Combines hierarchy changes, registration attribution, and sibling
    organisation verification into a single report.
    """
    return {
        "period": audit_period.cohort_number,
        "hierarchy_changes": reconcile_hierarchy_changes(audit_period),
        "registration_attribution": reconcile_registration_attribution(audit_period),
        "sibling_organisations": reconcile_sibling_organisations(audit_period),
    }