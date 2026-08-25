"""
Tests for the ``approve_audit_period_organisations`` management command.

The command reviews unapproved ``AuditPeriodOrganisation`` rows and lets the
audit team approve or decline each one. These tests exercise:

- the ``--dry-run`` exposure report (no writes);
- ``--auto-approve`` (approves every unapproved row, sets ``approved_at`` /
  ``approved_by``);
- the interactive prompt flow (approve / decline / skip / quit) via a patched
  ``input``;
- filtering by ``--cohort`` and ``--ods-code``;
- the approver validation (only RCPCH audit team / staff / superusers).

The seeded ``AuditPeriod`` rows come from the session-scoped
``seed_audit_periods_fixture`` in ``conftest.py``. The ``reorganisation``
fixture provides approved memberships for cohorts 8 and 9; we create our own
unapproved rows here so the command has something to review.
"""

from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodOrganisation,
)


APPROVED_AT = timezone.make_aware(
    timezone.datetime(2024, 1, 1, 0, 0, 0)
)


def _make_unapproved_membership(cohort_number, organisation, **overrides):
    """Create an unapproved AuditPeriodOrganisation row for an organisation."""
    period = AuditPeriod.objects.get(cohort_number=cohort_number)
    defaults = {
        "country": organisation.country,
        "trust": organisation.trust,
        "local_health_board": organisation.local_health_board,
        "integrated_care_board": organisation.integrated_care_board,
        "nhs_england_region": organisation.nhs_england_region,
        "openuk_network": organisation.openuk_network,
        "included_in_reporting": True,
        "source": "snapshot",
    }
    defaults.update(overrides)
    return AuditPeriodOrganisation.objects.create(
        audit_period=period,
        organisation=organisation,
        **defaults,
    )


@pytest.mark.django_db
def test_dry_run_reports_exposure_without_writing(GOSH):
    """--dry-run reports each unapproved row and its exposure but writes
    nothing (approved_at stays null)."""
    membership = _make_unapproved_membership(4, GOSH)

    out = StringIO()
    call_command("approve_audit_period_organisations", "--dry-run", stdout=out)

    output = out.getvalue()
    assert "Dry-run" in output
    assert GOSH.ods_code in output
    assert GOSH.name in output
    assert "No changes written" in output

    membership.refresh_from_db()
    assert membership.approved_at is None


@pytest.mark.django_db
def test_auto_approve_sets_approved_at_and_by(GOSH, e12_user_factory):
    """--auto-approve approves every unapproved row, setting approved_at and
    approved_by to the resolving user."""
    membership = _make_unapproved_membership(4, GOSH)
    approver = e12_user_factory(is_rcpch_audit_team_member=True)

    out = StringIO()
    call_command(
        "approve_audit_period_organisations",
        "--auto-approve",
        "--user",
        approver.email,
        stdout=out,
    )

    membership.refresh_from_db()
    assert membership.approved_at is not None
    assert membership.approved_by == approver
    assert "Approved 1 membership row(s)" in out.getvalue()


@pytest.mark.django_db
def test_auto_approve_skips_already_approved(GOSH, e12_user_factory):
    """--auto-approve only touches unapproved rows; already-approved rows are
    left untouched."""
    approver = e12_user_factory(is_rcpch_audit_team_member=True)
    already_approved = _make_unapproved_membership(
        4, GOSH, approved_at=APPROVED_AT, approved_by=approver
    )
    unapproved = _make_unapproved_membership(5, GOSH)

    out = StringIO()
    call_command(
        "approve_audit_period_organisations",
        "--auto-approve",
        "--user",
        approver.email,
        stdout=out,
    )

    already_approved.refresh_from_db()
    unapproved.refresh_from_db()
    # Already-approved row keeps its original approval timestamp.
    assert already_approved.approved_at == APPROVED_AT
    # Unapproved row is now approved.
    assert unapproved.approved_at is not None
    assert "Approved 1 membership row(s)" in out.getvalue()


@pytest.mark.django_db
def test_interactive_approve(GOSH, e12_user_factory):
    """Interactive mode approves a row when the user answers 'y'."""
    membership = _make_unapproved_membership(4, GOSH)
    approver = e12_user_factory(is_rcpch_audit_team_member=True)

    # First prompt is the approver email (blank -> we pass --user instead),
    # then the per-row approve prompt.
    with patch("builtins.input", side_effect=["y"]):
        out = StringIO()
        call_command(
            "approve_audit_period_organisations",
            "--user",
            approver.email,
            stdout=out,
        )

    membership.refresh_from_db()
    assert membership.approved_at is not None
    assert membership.approved_by == approver
    assert "Approved." in out.getvalue()


@pytest.mark.django_db
def test_interactive_decline_records_note(GOSH, e12_user_factory):
    """Declining a row leaves it unapproved and records the reason in notes."""
    membership = _make_unapproved_membership(4, GOSH)
    approver = e12_user_factory(is_rcpch_audit_team_member=True)

    with patch("builtins.input", side_effect=["n", "wrong trust"]):
        out = StringIO()
        call_command(
            "approve_audit_period_organisations",
            "--user",
            approver.email,
            stdout=out,
        )

    membership.refresh_from_db()
    assert membership.approved_at is None
    assert "wrong trust" in membership.notes


@pytest.mark.django_db
def test_interactive_skip_leaves_row_untouched(GOSH, e12_user_factory):
    """Skipping a row leaves it unapproved with no note."""
    membership = _make_unapproved_membership(4, GOSH)
    approver = e12_user_factory(is_rcpch_audit_team_member=True)

    with patch("builtins.input", side_effect=["s"]):
        out = StringIO()
        call_command(
            "approve_audit_period_organisations",
            "--user",
            approver.email,
            stdout=out,
        )

    membership.refresh_from_db()
    assert membership.approved_at is None
    assert membership.notes == ""
    assert "Skipped" in out.getvalue()


@pytest.mark.django_db
def test_interactive_quit_stops_processing(GOSH, e12_user_factory):
    """Quitting stops the review before later rows are processed."""
    first = _make_unapproved_membership(4, GOSH)
    second = _make_unapproved_membership(5, GOSH)
    approver = e12_user_factory(is_rcpch_audit_team_member=True)

    # Approve the first, then quit before the second.
    with patch("builtins.input", side_effect=["y", "q"]):
        out = StringIO()
        call_command(
            "approve_audit_period_organisations",
            "--user",
            approver.email,
            stdout=out,
        )

    first.refresh_from_db()
    second.refresh_from_db()
    assert first.approved_at is not None
    assert second.approved_at is None
    assert "Quit" in out.getvalue()


@pytest.mark.django_db
def test_cohort_filter_limits_rows(GOSH, ADDENBROOKES):
    """--cohort only reviews unapproved rows for that cohort."""
    _make_unapproved_membership(4, GOSH)
    _make_unapproved_membership(5, ADDENBROOKES)

    out = StringIO()
    call_command(
        "approve_audit_period_organisations",
        "--cohort",
        4,
        "--dry-run",
        stdout=out,
    )

    output = out.getvalue()
    assert GOSH.ods_code in output
    assert ADDENBROOKES.ods_code not in output


@pytest.mark.django_db
def test_ods_code_filter(GOSH, ADDENBROOKES):
    """--ods-code only reviews memberships for the specified organisation."""
    _make_unapproved_membership(4, GOSH)
    _make_unapproved_membership(4, ADDENBROOKES)

    out = StringIO()
    call_command(
        "approve_audit_period_organisations",
        "--ods-code",
        GOSH.ods_code,
        "--dry-run",
        stdout=out,
    )

    output = out.getvalue()
    assert GOSH.ods_code in output
    assert ADDENBROOKES.ods_code not in output


@pytest.mark.django_db
def test_no_unapproved_rows_reports_nothing(GOSH):
    """With no unapproved rows, the command reports nothing to review."""
    _make_unapproved_membership(4, GOSH, approved_at=APPROVED_AT)

    out = StringIO()
    call_command("approve_audit_period_organisations", "--dry-run", stdout=out)

    assert "No unapproved" in out.getvalue()


@pytest.mark.django_db
def test_approver_must_be_audit_team(GOSH, e12_user_factory):
    """A non-audit-team user cannot be recorded as the approver."""
    _make_unapproved_membership(4, GOSH)
    clinician = e12_user_factory(is_rcpch_audit_team_member=False)

    from django.core.management.base import CommandError

    with pytest.raises(CommandError, match="not an RCPCH audit-team member"):
        call_command(
            "approve_audit_period_organisations",
            "--auto-approve",
            "--user",
            clinician.email,
            stdout=StringIO(),
        )


@pytest.mark.django_db
def test_exposure_counts_registrations_and_cases(GOSH, e12_case_factory):
    """The exposure report counts registrations and distinct cases attached to
    the organisation."""
    _make_unapproved_membership(4, GOSH)
    # Two cases with a Site at GOSH; one registered, one not.
    e12_case_factory(
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )
    e12_case_factory(
        organisations__organisation=GOSH,
        registration=None,
    )

    out = StringIO()
    call_command(
        "approve_audit_period_organisations",
        "--dry-run",
        stdout=out,
    )

    output = out.getvalue()
    # 1 registration, 2 distinct cases.
    assert "Registrations (all periods): 1" in output
    assert "Distinct cases (all periods): 2" in output