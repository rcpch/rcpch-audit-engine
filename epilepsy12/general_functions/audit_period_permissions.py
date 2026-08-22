"""
Period-aware permission services.

These functions resolve user access for a specific ``AuditPeriod``. They are
the only functions that period-aware code (dashboard, case collections,
downloads, HTMX callbacks, publication) should call for permission decisions
that depend on historical affiliation. They must not fall back to current
``Organisation`` relationships.

Access model (see ``documentation/docs/development/audit-period-organisation.md``,
"Permission model" section):

1. **Direct organisation access** — a user with active employment at an
   organisation may access **all of that organisation's historical cases,
   irrespective of historical affiliation**. This is resolved through
   ``OrganisationIdentity``: a user employed at the current ODS code (e.g.
   ``RJZ30``) can access cases stored against a predecessor ODS code (e.g.
   ``RYQ30``) for any historical cohort, because both ``Organisation`` rows
   share the same ``OrganisationIdentity``. A reorganisation must not prevent
   an organisation from completing or reviewing its own historical records.

2. **Inherited Trust/LHB access** — a user elsewhere in a Trust or LHB may
   access Organisation A only for audit periods in which
   ``AuditPeriodOrganisation`` assigns Organisation A to that parent, **and
   only for the parent the user is currently affiliated with**. Inherited
   access is therefore current-affiliation-and-period-aware: a user at Trust B
   (Organisation A's current parent) can see Organisation A's cohort-9 cases
   (Trust B period) but not Organisation A's cohort-8 cases (Trust A period),
   even though Organisation A itself can see both. Inherited access never
   crosses the succession chain to a historical parent — that is direct access
   only.

3. **RCPCH access** — authorised RCPCH audit team and administrative users
   retain their broader access.

These functions are the source for route guards, dashboard selectors, HTMX
callbacks, downloads and direct clinical-record access. They are additive in
PR 3: only consumers explicitly migrated to them change behaviour. The
existing report-builder mixin and Organisational Audit permission paths are
unchanged.
"""

from __future__ import annotations

import logging
from typing import Iterable

from django.apps import apps

from .audit_period_hierarchy import (
    get_membership,
    MembershipMissing,
    MembershipUnapproved,
)

logger = logging.getLogger(__name__)


def _get_model(name: str):
    return apps.get_model("epilepsy12", name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_rcpch_user(user) -> bool:
    """Return True for authorised RCPCH audit team / staff / superusers.

    These users retain broader access that is not constrained by the
    period-aware affiliation rules.
    """
    if user is None:
        return False
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_rcpch_audit_team_member", False)
        or getattr(user, "is_rcpch_staff", False)
    )


def _user_is_active_and_confirmed(user) -> bool:
    """A user must be active and email-confirmed before any access decision.

    Superusers bypass the email-confirmation check (mirrors the existing
    ``lookup_user_permissions_on_child`` behaviour in ``decorator.py``).
    """
    if user is None:
        return False
    if getattr(user, "is_superuser", False):
        return bool(getattr(user, "is_active", False))
    return bool(
        getattr(user, "is_active", False)
        and getattr(user, "email_confirmed", False)
    )


def _active_employer_organisations(user) -> "Iterable":
    """Return the queryset of ``Organisation`` rows the user is actively
    employed at (``OrganisationEmployer.is_active=True``, no ``date_left``).

    A user's employment points at the **current** ``Organisation`` row (the
    ODS code in use today). Direct access to historical cases stored against
    a predecessor ODS code is resolved separately through
    ``OrganisationIdentity`` (see ``_user_organisation_identities``).
    """
    OrganisationEmployer = _get_model("OrganisationEmployer")
    return (
        OrganisationEmployer.objects.filter(
            epilepsy12_user=user,
            is_active=True,
            date_left__isnull=True,
        )
        .select_related("employer_organisation")
        .values_list("employer_organisation", flat=True)
    )


def _user_organisation_identities(user) -> "set[int]":
    """Return the set of ``OrganisationIdentity`` IDs the user is employed at.

    A user employed at the current ODS code (e.g. ``RJZ30``) gains direct
    access to cases stored against any predecessor ODS code that shares the
    same ``OrganisationIdentity`` (e.g. ``RYQ30``). If the employer has no
    ``identity`` FK (not yet backfilled), only the literal employer
    ``Organisation`` row counts.
    """
    Organisation = _get_model("Organisation")
    employer_ids = list(_active_employer_organisations(user))
    if not employer_ids:
        return set()

    employers = Organisation.objects.filter(pk__in=employer_ids).values_list(
        "pk", "identity"
    )
    identity_ids: set[int] = set()
    for _org_pk, identity_pk in employers:
        if identity_pk is not None:
            identity_ids.add(identity_pk)
    return identity_ids


def _user_current_parents(user) -> "dict[str, set[int]]":
    """Return the set of Trust and LHB IDs the user is currently affiliated
    with, resolved from the user's **active** employer organisations' current
    ``Organisation.trust`` / ``Organisation.local_health_board`` FKs.

    Inherited access is current-affiliation-and-period-aware: the user's
    current parent must match the parent recorded on the period's membership
    row. We deliberately read the current ``Organisation`` relationships here
    (not ``AuditPeriodOrganisation``) because inherited access follows the
    user's *current* affiliation, not the organisation's historical one.

    Returns a dict with two keys: ``"trust"`` and ``"local_health_board"``,
    each a set of IDs (possibly empty).
    """
    Organisation = _get_model("Organisation")
    employer_ids = list(_active_employer_organisations(user))
    if not employer_ids:
        return {"trust": set(), "local_health_board": set()}

    rows = Organisation.objects.filter(pk__in=employer_ids).values_list(
        "trust", "local_health_board"
    )
    trust_ids: set[int] = set()
    lhb_ids: set[int] = set()
    for trust_pk, lhb_pk in rows:
        if trust_pk is not None:
            trust_ids.add(trust_pk)
        if lhb_pk is not None:
            lhb_ids.add(lhb_pk)
    return {"trust": trust_ids, "local_health_board": lhb_ids}


def _organisation_shares_identity_with_user(organisation, user) -> bool:
    """Return True if ``organisation`` shares an ``OrganisationIdentity`` with
    any of the user's active employers.

    This is the direct-access resolution across ODS code changes: a user
    employed at ``RJZ30`` can access cases stored against ``RYQ30`` because
    both rows share the same ``OrganisationIdentity``. If the organisation
    has no ``identity`` FK, only a literal employer match counts (handled by
    the caller via ``_active_employer_organisations``).
    """
    if organisation.identity_id is None:
        return False
    user_identity_ids = _user_organisation_identities(user)
    return organisation.identity_id in user_identity_ids


# ---------------------------------------------------------------------------
# can_view_organisation_for_period
# ---------------------------------------------------------------------------


def can_view_organisation_for_period(user, organisation, audit_period) -> bool:
    """Return True if ``user`` may view ``organisation``'s data for
    ``audit_period``.

    The decision follows the three-tier access model:

    1. **RCPCH access** — superusers, RCPCH audit team members and RCPCH staff
       retain broader access, subject only to the user being active (and
       email-confirmed, unless a superuser).

    2. **Direct organisation access** — a user with active employment at the
       organisation may view **all** of that organisation's historical cases
       for any audit period, irrespective of historical affiliation. Access
       across an ODS code change is resolved through ``OrganisationIdentity``:
       a user employed at the current ODS code can view cases stored against
       a predecessor ODS code that shares the same identity. Direct access
       does **not** require an approved ``AuditPeriodOrganisation`` row to
       exist for the (organisation, period) pair — the organisation itself
       always retains access to its own historical records. (Reporting and
       publication consumers separately check membership readiness before
       publishing; the permission decision is about user access, not
       publication readiness.)

    3. **Inherited Trust/LHB access** — a user elsewhere in a Trust or LHB
       may view the organisation only for audit periods in which
       ``AuditPeriodOrganisation`` assigns the organisation to a parent the
       user is currently affiliated with. Inherited access is therefore
       current-affiliation-and-period-aware: a user at Trust B (the
       organisation's current parent) can see the organisation's cohort-9
       cases (Trust B period) but not its cohort-8 cases (Trust A period).
       Inherited access never crosses the succession chain to a historical
       parent — that is direct access only. Inherited access requires an
       approved membership row; an absent or unapproved membership denies
       inherited access (no fallback to current relationships).

    Inactive employment, unconfirmed email, absent membership rows and
    unapproved membership rows all deny access (except for RCPCH users, who
    bypass the affiliation rules).
    """
    if not _user_is_active_and_confirmed(user):
        return False

    if _is_rcpch_user(user):
        return True

    # Direct organisation access — the organisation itself retains access to
    # its own historical records across all periods and ODS code changes.
    employer_ids = set(_active_employer_organisations(user))
    if organisation.pk in employer_ids:
        return True
    if _organisation_shares_identity_with_user(organisation, user):
        return True

    # Inherited Trust/LHB access — current-affiliation-and-period-aware.
    try:
        membership = get_membership(organisation, audit_period)
    except (MembershipMissing, MembershipUnapproved):
        # No approved membership row -> no inherited access. Direct access
        # was already checked above; if that also failed, the user is denied.
        return False

    user_parents = _user_current_parents(user)
    if membership.trust_id is not None and membership.trust_id in user_parents["trust"]:
        return True
    if (
        membership.local_health_board_id is not None
        and membership.local_health_board_id in user_parents["local_health_board"]
    ):
        return True

    return False


# ---------------------------------------------------------------------------
# Bulk access queries
# ---------------------------------------------------------------------------
#
# These return the set of periods / memberships / organisations a user may
# view. They are the source for dashboard selectors, parent dropdowns and
# case-list querysets. They must return only rows the user is authorised to
# see under the same three-tier model as ``can_view_organisation_for_period``.


def _user_direct_organisation_ids(user) -> "set[int]":
    """Return the set of ``Organisation`` IDs the user has direct access to.

    This is the user's active employers plus every other ``Organisation``
    row that shares an ``OrganisationIdentity`` with one of those employers
    (the ODS code succession chain). A user employed at ``RJZ30`` gains
    direct access to ``RYQ30`` (and any further predecessors) via the shared
    identity.

    Returns an empty set for users with no active employer.
    """
    Organisation = _get_model("Organisation")
    employer_ids = set(_active_employer_organisations(user))
    if not employer_ids:
        return set()

    identity_ids = _user_organisation_identities(user)
    direct_ids = set(employer_ids)
    if identity_ids:
        direct_ids.update(
            Organisation.objects.filter(identity_id__in=identity_ids).values_list(
                "pk", flat=True
            )
        )
    return direct_ids


def _organisation_identity_chain_ids(organisation) -> "set[int]":
    """Return the set of ``Organisation`` IDs that share the same
    ``OrganisationIdentity`` as ``organisation``, including ``organisation``
    itself.

    This is the ODS code succession chain: for PRUH, it returns both RYQ30
    and RJZ30 (and any further predecessors/successors) because they share
    the same identity. If ``organisation`` has no ``identity`` FK, only the
    literal organisation is returned.
    """
    Organisation = _get_model("Organisation")
    if organisation.identity_id is None:
        return {organisation.pk}
    return set(
        Organisation.objects.filter(
            identity_id=organisation.identity_id
        ).values_list("pk", flat=True)
    )


def get_accessible_periods(user, organisation):
    """Return the ``AuditPeriod`` instances the user may view for the given
    organisation.

    - RCPCH users: every period that has an approved, included membership
      for the organisation (i.e. the periods the organisation participated
      in). RCPCH users do not see periods with no membership row, because
      there is nothing to report for those periods.
    - Direct users (employed at the organisation or sharing its identity):
      every period that has an approved, included membership for the
      organisation. Direct access is period-independent in principle, but
      the accessible-periods query exists to populate selectors, and a
      period with no membership row has no dashboard summary to show. A
      direct user retains access to their own historical cases for any
      period via the case/registration path (``can_edit_case_for_period``),
      even if the period is not returned here.
    - Inherited users: only the periods in which the organisation's
      approved membership assigns it to a parent the user is currently
      affiliated with.

    Returns a queryset of ``AuditPeriod`` instances, ordered by cohort
    number descending (most recent first), which is the order dashboard
    cohort selectors expect.
    """
    AuditPeriod = _get_model("AuditPeriod")
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    if not _user_is_active_and_confirmed(user):
        return AuditPeriod.objects.none()

    if _is_rcpch_user(user):
        # RCPCH users see every period the organisation participated in,
        # resolved across the identity chain (RYQ30's cohort 8 membership
        # counts for PRUH even when the caller passed RJZ30).
        chain_ids = _organisation_identity_chain_ids(organisation)
        period_ids = AuditPeriodOrganisation.objects.filter(
            organisation_id__in=chain_ids,
            approved_at__isnull=False,
            included_in_reporting=True,
        ).values_list("audit_period", flat=True)
        return AuditPeriod.objects.filter(pk__in=period_ids).order_by(
            "-cohort_number"
        )

    direct_ids = _user_direct_organisation_ids(user)
    if organisation.pk in direct_ids:
        # Direct access — see every period the organisation participated in,
        # resolved across the identity chain (a direct user at RJZ30 sees
        # RYQ30's cohort 8 membership because both share the same identity).
        chain_ids = _organisation_identity_chain_ids(organisation)
        period_ids = AuditPeriodOrganisation.objects.filter(
            organisation_id__in=chain_ids,
            approved_at__isnull=False,
            included_in_reporting=True,
        ).values_list("audit_period", flat=True)
        return AuditPeriod.objects.filter(pk__in=period_ids).order_by(
            "-cohort_number"
        )

    # Inherited access — only periods whose membership parent matches the
    # user's current affiliation. Resolve across the identity chain so a
    # dashboard passing the current ODS code (RJZ30) still finds the
    # predecessor's cohort 8 membership (RYQ30) if the user's current parent
    # is Trust A.
    user_parents = _user_current_parents(user)
    parent_q = _build_parent_q(user_parents)
    if parent_q is None:
        return AuditPeriod.objects.none()

    chain_ids = _organisation_identity_chain_ids(organisation)
    period_ids = (
        AuditPeriodOrganisation.objects.filter(
            organisation_id__in=chain_ids,
            approved_at__isnull=False,
            included_in_reporting=True,
        )
        .filter(parent_q)
        .values_list("audit_period", flat=True)
    )
    return AuditPeriod.objects.filter(pk__in=period_ids).order_by("-cohort_number")


def get_accessible_memberships(user, audit_period):
    """Return the ``AuditPeriodOrganisation`` rows the user may view for the
    given audit period.

    - RCPCH users: every approved, included membership for the period.
    - Direct users: their own organisation's memberships for the period
      (resolved across the ``OrganisationIdentity`` chain), regardless of
      parent. Plus any inherited memberships (see below).
    - Inherited users: memberships whose Trust or LHB matches the user's
      current affiliation.

    A non-RCPCH user with both direct and inherited access (e.g. a user
    employed at Organisation A who is also elsewhere in Trust B) gets the
    union of both sets: their own organisation's memberships plus sibling
    organisations under their current parent.

    Returns a queryset of ``AuditPeriodOrganisation`` instances, with
    ``organisation`` and the hierarchy FKs select_related for template
    rendering.
    """
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    base_qs = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=False,
        included_in_reporting=True,
    ).select_related(
        "organisation",
        "country",
        "trust",
        "local_health_board",
        "integrated_care_board",
        "nhs_england_region",
        "openuk_network",
    )

    if not _user_is_active_and_confirmed(user):
        return AuditPeriodOrganisation.objects.none()

    if _is_rcpch_user(user):
        return base_qs

    direct_ids = _user_direct_organisation_ids(user)
    user_parents = _user_current_parents(user)
    parent_q = _build_parent_q(user_parents)

    # Union of direct (own organisation across the identity chain) and
    # inherited (siblings under the user's current parent).
    if direct_ids and parent_q is not None:
        return base_qs.filter(_build_direct_or_inherited_q(direct_ids, parent_q))
    if direct_ids:
        return base_qs.filter(organisation_id__in=direct_ids)
    if parent_q is not None:
        return base_qs.filter(parent_q)
    return AuditPeriodOrganisation.objects.none()


def get_accessible_organisations(user, audit_period, parent=None):
    """Return the ``Organisation`` instances the user may view for the given
    audit period.

    - RCPCH users: every organisation with an approved, included membership
      for the period.
    - Direct users: their own organisation(s) (across the identity chain)
      that have an approved, included membership for the period, plus any
      sibling organisations under their current parent.
    - Inherited users: organisations whose approved membership for the
      period assigns them to a parent the user is currently affiliated
      with.

    If ``parent`` is supplied, the result is further narrowed to
    organisations whose membership for the period assigns them to that
    parent. ``parent`` is a model instance (``Trust``, ``LocalHealthBoard``,
    ``IntegratedCareBoard``, ``NHSEnglandRegion``, ``OPENUKNetwork`` or
    ``Country``); the parent type is inferred from the instance's model.

    Returns a queryset of ``Organisation`` instances, ordered by name.
    """
    Organisation = _get_model("Organisation")
    AuditPeriodOrganisation = _get_model("AuditPeriodOrganisation")

    if not _user_is_active_and_confirmed(user):
        return Organisation.objects.none()

    membership_qs = AuditPeriodOrganisation.objects.filter(
        audit_period=audit_period,
        approved_at__isnull=False,
        included_in_reporting=True,
    )

    if _is_rcpch_user(user):
        org_ids = membership_qs.values_list("organisation", flat=True)
    else:
        direct_ids = _user_direct_organisation_ids(user)
        user_parents = _user_current_parents(user)
        parent_q = _build_parent_q(user_parents)

        if direct_ids and parent_q is not None:
            org_ids = membership_qs.filter(
                _build_direct_or_inherited_q(direct_ids, parent_q)
            ).values_list("organisation", flat=True)
        elif direct_ids:
            org_ids = membership_qs.filter(
                organisation_id__in=direct_ids
            ).values_list("organisation", flat=True)
        elif parent_q is not None:
            org_ids = membership_qs.filter(parent_q).values_list(
                "organisation", flat=True
            )
        else:
            return Organisation.objects.none()

    qs = Organisation.objects.filter(pk__in=org_ids)

    if parent is not None:
        parent_field = _parent_field_for_instance(parent)
        if parent_field is None:
            return Organisation.objects.none()
        # Narrow to organisations whose membership for the period assigns
        # them to this parent.
        parent_org_ids = membership_qs.filter(**{parent_field: parent}).values_list(
            "organisation", flat=True
        )
        qs = qs.filter(pk__in=parent_org_ids)

    return qs.distinct().order_by("name")


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def _build_parent_q(user_parents) -> "object | None":
    """Build a ``Q`` object matching memberships whose Trust or LHB is in the
    user's current parents.

    Returns ``None`` if the user has no current parents (no inherited access
    possible).
    """
    from django.db.models import Q

    trust_ids = user_parents["trust"]
    lhb_ids = user_parents["local_health_board"]
    clauses = []
    if trust_ids:
        clauses.append(Q(trust_id__in=trust_ids))
    if lhb_ids:
        clauses.append(Q(local_health_board_id__in=lhb_ids))
    if not clauses:
        return None
    q = clauses[0]
    for clause in clauses[1:]:
        q = q | clause
    return q


def _build_direct_or_inherited_q(direct_ids, parent_q):
    """Build a ``Q`` object matching memberships that are either the user's
    direct organisation (across the identity chain) OR under a parent the
    user is currently affiliated with.
    """
    from django.db.models import Q

    return Q(organisation_id__in=direct_ids) | parent_q


def _parent_field_for_instance(parent) -> "str | None":
    """Return the ``AuditPeriodOrganisation`` FK field name for a parent
    model instance, or ``None`` if the instance is not a recognised parent
    type.
    """
    parent_model_name = parent.__class__.__name__
    return {
        "Trust": "trust",
        "LocalHealthBoard": "local_health_board",
        "IntegratedCareBoard": "integrated_care_board",
        "NHSEnglandRegion": "nhs_england_region",
        "OPENUKNetwork": "openuk_network",
        "Country": "country",
    }.get(parent_model_name)
