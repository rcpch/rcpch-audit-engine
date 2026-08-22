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
