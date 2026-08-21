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


def get_participating_organisations(audit_period):
    """Return the organisations that participate in reporting for the given
    audit period.

    An organisation participates if it has an approved, included
    ``AuditPeriodOrganisation`` row for the period. Organisations with
    unapproved or excluded memberships are not returned.

    Returns a queryset of ``Organisation`` instances.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
    return (
        AuditPeriodOrganisation.objects.filter(
            audit_period=audit_period,
            approved_at__isnull=False,
            included_in_reporting=True,
        )
        .select_related("organisation")
        .values_list("organisation", flat=True)
    )


def get_expected_reporting_hierarchies(audit_period) -> dict[str, Any]:
    """Return the distinct reporting hierarchies that apply across all
    participating organisations for the given audit period.

    Useful for populating parent-level selectors and for verifying that the
    period's memberships cover the expected set of trusts, ICBs, regions,
    networks and countries.

    Returns a dict keyed by hierarchy field name (``"trust"``,
    ``"local_health_board"``, ``"integrated_care_board"``,
    ``"nhs_england_region"``, ``"openuk_network"``, ``"country"``). Each value
    is a list of the distinct model instances of that hierarchy type used by
    approved, included memberships for the period. Hierarchy fields that no
    participating organisation uses (e.g. ``local_health_board`` for an
    all-English period) return an empty list.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    memberships = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=False,
        included_in_reporting=True,
    )

    hierarchies: dict[str, list[Any]] = {}
    for field in (
        "country",
        "trust",
        "local_health_board",
        "integrated_care_board",
        "nhs_england_region",
        "openuk_network",
    ):
        # values_list with flat=True on a nullable FK returns [None, ...] for
        # organisations without that hierarchy; filter those out.
        ids = [
            pk
            for pk in memberships.values_list(field, flat=True).distinct()
            if pk is not None
        ]
        model_name = {
            "country": "Country",
            "trust": "Trust",
            "local_health_board": "LocalHealthBoard",
            "integrated_care_board": "IntegratedCareBoard",
            "nhs_england_region": "NHSEnglandRegion",
            "openuk_network": "OPENUKNetwork",
        }[field]
        model = _get_model(model_name)
        hierarchies[field] = list(model.objects.filter(pk__in=ids))

    return hierarchies


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
    """Return True if the audit period is ready for period-aware reporting.

    A period is ready when **both** of the following hold:

    1. Every ``AuditPeriodOrganisation`` row for the period is approved —
       there are no unapproved candidate rows.
    2. Every organisation that has at least one registration in the period
       has a membership row (no orphaned registrations).

    The first condition catches sync-sourced candidate rows that the audit
    team have not yet reviewed, even for organisations that have no
    registrations in the period (e.g. an organisation that participated in
    the audit but has no recruited cases in this period). The previous
    definition only checked organisations with registrations, which meant
    an unapproved membership row for a zero-registration organisation would
    not block readiness — that is not fit for purpose, because publication
    and dashboard selectors iterate over membership rows, not registrations.

    A period with no membership rows at all is considered not ready unless
    it also has no registrations, in which case there is nothing to report
    and the period is trivially ready.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")
    Registration = _get_model("Registration")

    # Condition 1: no unapproved membership rows for the period.
    has_unapproved = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=True,
    ).exists()
    if has_unapproved:
        return False

    # Condition 2: every organisation with a registration has a membership
    # row (approved, since condition 1 already passed).
    participating_org_ids = set(
        Registration.objects.filter(
            audit_period=audit_period
        ).values_list("case__epilepsy12_sites__organisation", flat=True).distinct()
    )

    if not participating_org_ids:
        # No registrations in this period — nothing to block readiness.
        return True

    approved_org_ids = set(
        AuditPeriodOrganisation.objects.filter(
            audit_period=audit_period,
            approved_at__isnull=False,
            organisation_id__in=participating_org_ids,
        ).values_list("organisation_id", flat=True)
    )

    return participating_org_ids.issubset(approved_org_ids)


def period_readiness_report(audit_period) -> dict[str, Any]:
    """Return a detailed readiness report for the given audit period.

    The report includes:
    - ``ready``: bool — True if the period is ready (see ``is_period_ready``):
      no unapproved membership rows, and every organisation with a
      registration has an approved membership row.
    - ``participating_organisations``: list of organisation IDs that have
      at least one registration in the period.
    - ``approved_memberships``: list of organisation IDs with approved
      membership rows.
    - ``unapproved_memberships``: list of organisation IDs with a membership
      row that has not been approved.
    - ``missing_memberships``: list of organisation IDs with a registration
      in the period but no membership row.
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
        "ready": not unapproved_org_ids and not missing_org_ids,
        "participating_organisations": sorted(participating_org_ids),
        "approved_memberships": sorted(approved_org_ids),
        "missing_memberships": sorted(missing_org_ids),
        "unapproved_memberships": sorted(unapproved_org_ids),
    }