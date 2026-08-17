"""
Period-aware hierarchy service layer.

These functions resolve organisational hierarchy for a specific
``AuditPeriod``. They are the only functions that period-aware code
(dashboard, permissions, aggregation, publication) should call for
hierarchy resolution. They must not fall back to current ``Organisation``
relationships.

See ``documentation/docs/development/audit-period-organisation.md`` for the
full design.
"""

from __future__ import annotations

import logging
from typing import Any

from django.apps import apps

logger = logging.getLogger(__name__)


class MembershipError(Exception):
    """Base class for membership-resolution errors."""


class MembershipMissing(MembershipError):
    """No ``AuditPeriodOrganisation`` row exists for the given
    (organisation, audit_period) pair."""


class MembershipUnapproved(MembershipError):
    """A membership row exists but has not been approved by the audit team."""


def _get_model(name: str):
    return apps.get_model("epilepsy12", name)


def get_membership(organisation, audit_period):
    """Return the approved ``AuditPeriodOrganisation`` for the given
    organisation and audit period.

    Raises:
        MembershipMissing: if no row exists.
        MembershipUnapproved: if a row exists but ``approved_at`` is None.

    This function must not fall back to current ``Organisation``
    relationships. Period-aware code must call this (or a wrapper) and
    handle the error explicitly.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    try:
        membership = AuditPeriodOrganisation.objects.select_related(
            "audit_period",
            "organisation",
            "country",
            "trust",
            "local_health_board",
            "integrated_care_board",
            "nhs_england_region",
            "openuk_network",
        ).get(
            organisation=organisation,
            audit_period=audit_period,
        )
    except AuditPeriodOrganisation.DoesNotExist:
        raise MembershipMissing(
            f"No AuditPeriodOrganisation for {organisation} in {audit_period}."
        )

    if membership.approved_at is None:
        raise MembershipUnapproved(
            f"AuditPeriodOrganisation for {organisation} in {audit_period} "
            "has not been approved."
        )

    return membership


def get_reporting_hierarchy(organisation, audit_period):
    """Return a dict of the hierarchy entities for the given organisation
    and audit period.

    Keys: ``country``, ``trust``, ``local_health_board``,
    ``integrated_care_board``, ``nhs_england_region``, ``openuk_network``.
    Values are model instances or ``None``.

    Raises ``MembershipMissing`` or ``MembershipUnapproved`` if the
    membership row is absent or unapproved.
    """
    membership = get_membership(organisation, audit_period)
    return {
        "country": membership.country,
        "trust": membership.trust,
        "local_health_board": membership.local_health_board,
        "integrated_care_board": membership.integrated_care_board,
        "nhs_england_region": membership.nhs_england_region,
        "openuk_network": membership.openuk_network,
    }


def get_organisations_for_parent(parent, audit_period, parent_field: str):
    """Return all organisations whose approved membership for the given
    audit period assigns them to the given parent.

    ``parent_field`` is one of ``"trust"``, ``"local_health_board"``,
    ``"integrated_care_board"``, ``"nhs_england_region"``,
    ``"openuk_network"``, ``"country"``.

    Only approved, included memberships are returned.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    return AuditPeriodOrganisation.objects.filter(
        **{
            parent_field: parent,
            "audit_period": audit_period,
            "approved_at__isnull": False,
            "included_in_reporting": True,
        }
    ).select_related("organisation")


def get_sibling_organisations(organisation, audit_period):
    """Return the sibling organisations for the given organisation and
    audit period — other organisations that share the same Trust or Local
    Health Board in that period.

    The organisation itself is excluded from the result.

    Raises ``MembershipMissing`` or ``MembershipUnapproved`` if the
    organisation has no approved membership for the period.
    """
    membership = get_membership(organisation, audit_period)

    if membership.trust is not None:
        parent_field = "trust"
        parent = membership.trust
    elif membership.local_health_board is not None:
        parent_field = "local_health_board"
        parent = membership.local_health_board
    else:
        # No trust or LHB — the organisation has no siblings in the
        # administrative hierarchy (e.g. Jersey, which is both an
        # organisation and a trust).
        return []

    siblings = get_organisations_for_parent(parent, audit_period, parent_field)
    return [m.organisation for m in siblings if m.organisation_id != organisation.id]


def is_period_ready(audit_period) -> bool:
    """Return True if every participating organisation for the given
    audit period has an approved membership row.

    An organisation is "participating" if it has at least one registration
    in the audit period. This is a pragmatic definition: the sync may not
    create rows for organisations that never participated in a historical
    period, and we don't want to block readiness on those.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
    Registration = _get_model("Registration")

    # Organisations that have at least one registration in this period.
    participating_org_ids = set(
        Registration.objects.filter(
            audit_period=audit_period
        ).values_list("case__epilepsy12_sites__organisation", flat=True).distinct()
    )

    if not participating_org_ids:
        # No registrations in this period — nothing to block readiness.
        return True

    # Approved memberships for this period, for participating organisations.
    approved_org_ids = set(
        AuditPeriodOrganisation.objects.filter(
            audit_period=audit_period,
            approved_at__isnull=False,
            organisation_id__in=participating_org_ids,
        ).values_list("organisation_id", flat=True)
    )

    # Every participating organisation must have an approved membership.
    return participating_org_ids.issubset(approved_org_ids)


def period_readiness_report(audit_period) -> dict[str, Any]:
    """Return a detailed readiness report for the given audit period.

    The report includes:
    - ``ready``: bool — True if every participating organisation has an
      approved membership.
    - ``participating_organisations``: list of organisation IDs that have
      at least one registration in the period.
    - ``approved_memberships``: list of organisation IDs with approved
      membership rows.
    - ``missing_memberships``: list of organisation IDs with no membership
      row.
    - ``unapproved_memberships``: list of organisation IDs with a membership
      row that has not been approved.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
    Registration = _get_model("Registration")

    participating_org_ids = set(
        Registration.objects.filter(
            audit_period=audit_period
        ).values_list("case__epilepsy12_sites__organisation", flat=True).distinct()
    )

    memberships = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        organisation_id__in=participating_org_ids,
    )

    approved_org_ids = set()
    unapproved_org_ids = set()
    for m in memberships:
        if m.approved_at is not None:
            approved_org_ids.add(m.organisation_id)
        else:
            unapproved_org_ids.add(m.organisation_id)

    missing_org_ids = participating_org_ids - approved_org_ids - unapproved_org_ids

    return {
        "ready": not missing_org_ids and not unapproved_org_ids,
        "participating_organisations": sorted(participating_org_ids),
        "approved_memberships": sorted(approved_org_ids),
        "missing_memberships": sorted(missing_org_ids),
        "unapproved_memberships": sorted(unapproved_org_ids),
    }