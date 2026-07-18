"""
Tests for Epilepsy12User model-level invariants.

Covers syncing / enforcement of fields that must remain consistent across
whichever code path creates or updates a user (manager, factory, form, view).

Currently focuses on the `view_preference` invariant: the national scope (2)
is only permitted on users who are also a superuser or an RCPCH audit team
member. Any other user attempting to set national view is silently downgraded
to organisation level (0) by the model's save() hook.
"""

# Standard imports
import pytest

# RCPCH imports
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_ADMINISTRATOR,
    RCPCH_AUDIT_TEAM,
)
from epilepsy12.models import Epilepsy12User


@pytest.mark.django_db
class TestViewPreferenceNationalSync:
    """view_preference == 2 (national) must be gated on superuser or
    is_rcpch_audit_team_member, enforced at the model layer."""

    def test_national_view_preference_downgraded_for_plain_user(
        self, seed_groups_fixture
    ):
        """A non-superuser, non-RCPCH-audit-team user cannot keep national view."""
        user = Epilepsy12User(
            email="plain@example.com",
            first_name="Plain",
            surname="User",
            role=AUDIT_CENTRE_ADMINISTRATOR,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_rcpch_audit_team_member=False,
            view_preference=2,  # national - should be rejected
        )
        user.set_password("pw")
        user.save()

        user.refresh_from_db()
        assert user.view_preference == 0  # silently downgraded to organisation

    def test_national_view_preference_allowed_for_rcpch_audit_team_member(
        self, seed_groups_fixture
    ):
        """RCPCH audit team members may keep national view."""
        user = Epilepsy12User(
            email="audit_team@example.com",
            first_name="Audit",
            surname="Team",
            role=RCPCH_AUDIT_TEAM,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_rcpch_audit_team_member=True,
            view_preference=2,
        )
        user.set_password("pw")
        user.save()

        user.refresh_from_db()
        assert user.view_preference == 2

    def test_national_view_preference_allowed_for_superuser(self, seed_groups_fixture):
        """Superusers may keep national view even if not flagged as audit team."""
        user = Epilepsy12User(
            email="super@example.com",
            first_name="Super",
            surname="User",
            role=RCPCH_AUDIT_TEAM,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            is_rcpch_audit_team_member=False,
            view_preference=2,
        )
        user.set_password("pw")
        user.save()

        user.refresh_from_db()
        assert user.view_preference == 2

    def test_national_view_preference_downgraded_on_update(self, seed_groups_fixture):
        """An existing plain user who is later set to national gets downgraded."""
        user = Epilepsy12User(
            email="update@example.com",
            first_name="Update",
            surname="User",
            role=AUDIT_CENTRE_ADMINISTRATOR,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_rcpch_audit_team_member=False,
            view_preference=0,
        )
        user.set_password("pw")
        user.save()

        # Later, something tries to escalate to national without granting the
        # required flags.
        user.view_preference = 2
        user.save(update_fields=["view_preference"])

        user.refresh_from_db()
        assert user.view_preference == 0

    def test_national_view_preference_kept_when_promoted_to_audit_team(
        self, seed_groups_fixture
    ):
        """Once a user becomes an RCPCH audit team member, national is honoured."""
        user = Epilepsy12User(
            email="promote@example.com",
            first_name="Promote",
            surname="User",
            role=AUDIT_CENTRE_ADMINISTRATOR,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_rcpch_audit_team_member=False,
            view_preference=0,
        )
        user.set_password("pw")
        user.save()

        user.is_rcpch_audit_team_member = True
        user.role = RCPCH_AUDIT_TEAM
        user.view_preference = 2
        user.save(update_fields=["is_rcpch_audit_team_member", "role", "view_preference"])

        user.refresh_from_db()
        assert user.view_preference == 2
