"""
Tests for the ``audit_rcpch_user_flags`` management command.

The command is a read-only report of users whose RCPCH flags, role and groups
disagree. The test database already contains seeded users, so each test checks
only for the users it creates.
"""

import csv
from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_TEAM,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
)
from epilepsy12.management.commands.audit_rcpch_user_flags import (
    FLAG_WITHOUT_ROLE,
    GROUP_MISMATCH,
    ROLE_WITHOUT_FLAG,
)


def _csv_rows_by_email(*args):
    out = StringIO()
    call_command("audit_rcpch_user_flags", "--csv", *args, stdout=out)
    return {row["email"]: row for row in csv.DictReader(StringIO(out.getvalue()))}


def _findings(row):
    return set(row["findings"].split(";"))


@pytest.mark.django_db
def test_consistent_audit_team_user_is_not_reported(e12_user_factory):
    user = e12_user_factory(
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        groups=[Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert user.email not in _csv_rows_by_email()


@pytest.mark.django_db
def test_consistent_clinician_is_not_reported(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert user.email not in _csv_rows_by_email()


@pytest.mark.django_db
def test_clinician_with_audit_team_flag_is_reported(e12_user_factory):
    """The main risk: a clinician with the flag loses national access."""
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=True,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    row = _csv_rows_by_email()[user.email]
    assert _findings(row) == {FLAG_WITHOUT_ROLE}
    assert row["expected_group"] == TRUST_AUDIT_TEAM_FULL_ACCESS


@pytest.mark.django_db
def test_staff_flag_alone_is_reported(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_staff=True,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert _findings(_csv_rows_by_email()[user.email]) == {FLAG_WITHOUT_ROLE}


@pytest.mark.django_db
def test_audit_team_role_without_flags_is_reported(e12_user_factory):
    user = e12_user_factory(
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=False,
        groups=[Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert _findings(_csv_rows_by_email()[user.email]) == {ROLE_WITHOUT_FLAG}


@pytest.mark.django_db
def test_wrong_or_extra_groups_are_reported(e12_user_factory):
    wrong_group = e12_user_factory(
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)],
    )
    extra_group = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        groups=[
            Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS),
            Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS),
        ],
    )
    no_group = e12_user_factory(role=AUDIT_CENTRE_LEAD_CLINICIAN)

    rows = _csv_rows_by_email()
    for user in (wrong_group, extra_group, no_group):
        assert _findings(rows[user.email]) == {GROUP_MISMATCH}


@pytest.mark.django_db
def test_active_only_skips_inactive_users(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=True,
        is_active=False,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert user.email in _csv_rows_by_email()
    assert user.email not in _csv_rows_by_email("--active-only")


@pytest.mark.django_db
def test_text_report_and_no_writes(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=True,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )
    updated_at = user.updated_at

    out = StringIO()
    call_command("audit_rcpch_user_flags", stdout=out)

    assert user.email in out.getvalue()
    assert "will LOSE national access" in out.getvalue()
    user.refresh_from_db()
    assert user.updated_at == updated_at
    assert user.is_rcpch_audit_team_member is True


@pytest.mark.django_db
def test_csv_output_file(e12_user_factory, tmp_path):
    user = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=True,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )
    output = tmp_path / "report.csv"

    call_command(
        "audit_rcpch_user_flags", "--csv", "--output", str(output), stderr=StringIO()
    )

    with open(output, newline="") as handle:
        emails = {row["email"] for row in csv.DictReader(handle)}
    assert user.email in emails
