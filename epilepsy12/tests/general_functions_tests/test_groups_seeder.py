"""
Tests for ``groups_seeder()`` (epilepsy12/management/commands/create_groups.py).

The seeder is the single source of truth for which Django permissions each E12
group holds. View tests exercise those permissions indirectly, but only for the
flows they happen to cover — a permission dropped from the seeder can go
unnoticed until an unrelated view test fails in a fresh database (CI), while a
reused local test DB keeps the previously-seeded permission and stays green.

These tests pin the expected permission sets directly against the seeder, so
changing a group's permissions is a deliberate act that fails here first.
"""

import pytest
from django.contrib.auth.models import Group

from epilepsy12.constants.user_types import (
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    PATIENT_ACCESS,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    GROUPS,
)
from epilepsy12.management.commands.create_groups import groups_seeder


@pytest.fixture
def seeded_groups(django_db_setup, django_db_blocker):
    """Run the seeder once against the test DB and return the groups."""
    with django_db_blocker.unblock():
        groups_seeder(verbose=False)
    return Group.objects.all()


def _codenames(group):
    return set(group.permissions.values_list("codename", flat=True))


@pytest.mark.django_db
def test_all_groups_created(seeded_groups):
    """Every group in GROUPS exists after seeding."""
    assert set(seeded_groups.values_list("name", flat=True)) == set(GROUPS)


@pytest.mark.django_db
def test_view_only_group_can_create_and_update_cases(seeded_groups):
    """
    trust_audit_team_view_only (audit centre administrators) must hold
    add_case and change_case: "view only" refers to clinical records, not
    case demographics. This was dropped in a seeder refactor and only
    surfaced as a permission_required 302 in CI's fresh database.
    """
    view_only = seeded_groups.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)

    assert {"add_case", "change_case"} <= _codenames(view_only)
    # ...but cannot delete them
    assert "delete_case" not in _codenames(view_only)


@pytest.mark.django_db
def test_view_only_group_has_view_permissions(seeded_groups):
    view_only = seeded_groups.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
    codenames = _codenames(view_only)

    assert "view_case" in codenames
    assert "view_registration" in codenames
    # no editor-level permissions
    assert "delete_epilepsy12user" not in codenames


@pytest.mark.django_db
def test_edit_access_group(seeded_groups):
    edit = seeded_groups.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
    codenames = _codenames(edit)

    assert {"add_case", "change_case"} <= codenames
    assert "delete_case" in codenames  # editors can delete patients
    assert "view_case" in codenames


@pytest.mark.django_db
def test_full_access_group(seeded_groups):
    full = seeded_groups.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
    codenames = _codenames(full)

    assert {"add_case", "change_case", "delete_case"} <= codenames
    # lead clinicians can transfer lead centre
    assert "can_transfer_epilepsy12_lead_centre" in codenames


@pytest.mark.django_db
def test_audit_team_group_custom_permissions(seeded_groups):
    """The RCPCH audit team group holds all the custom E12 permissions."""
    audit_team = seeded_groups.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
    codenames = _codenames(audit_team)

    assert "can_publish_epilepsy12_data" in codenames
    assert "can_extend_submission_deadline" in codenames
    assert "can_reset_two_factor_authentication" in codenames
    assert "can_transfer_epilepsy12_lead_centre" in codenames
    # plus everything the clinical groups hold
    assert {"view_case", "add_case", "change_case", "delete_case"} <= codenames


@pytest.mark.django_db
def test_patient_access_group(seeded_groups):
    patient = seeded_groups.get(name=PATIENT_ACCESS)
    codenames = _codenames(patient)

    assert "can_consent_to_audit_participation" in codenames
    assert "view_case" in codenames
    # nothing else
    assert "add_case" not in codenames


@pytest.mark.django_db
def test_seeder_is_idempotent(seeded_groups):
    """Re-running the seeder neither duplicates permissions nor errors."""
    audit_team = seeded_groups.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
    permission_count = audit_team.permissions.count()

    groups_seeder(verbose=False)

    audit_team.refresh_from_db()
    assert audit_team.permissions.count() == permission_count
    assert Group.objects.filter(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS).count() == 1
