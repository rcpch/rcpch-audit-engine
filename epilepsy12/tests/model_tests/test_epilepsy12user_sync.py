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

# Django imports
from django.contrib.auth import get_user_model

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


@pytest.mark.django_db
class TestCreateSuperuserDefaults:
    """create_superuser must produce a fully-privileged RCPCH user.

    Regression test: an early ``setdefault("is_rcpch_staff", False)`` shadowed
    the intended ``setdefault("is_rcpch_staff", True)`` later in the method, so
    superusers created via the manager ended up NOT being RCPCH staff. That
    then tripped the RCPCH-staff-only check guarding the create-rcpch-staff
    route (see test_permissions_create.py), 403-ing superusers on the "Add a
    new RCPCH Staff User" button. It also meant ``manage.py createsuperuser``
    (which passes no organisation_employer) raised a ValueError in
    create_user, since only RCPCH staff may be created without an employer.
    """

    def test_create_superuser_defaults_rcpch_flags(self, seed_groups_fixture):
        """Superusers are RCPCH staff and RCPCH audit team members by default."""
        user_model = get_user_model()

        # No organisation_employer passed: mirrors how `manage.py
        # createsuperuser` invokes the manager (REQUIRED_FIELDS only).
        superuser = user_model.objects.create_superuser(
            email="new_superuser@example.com",
            password="Ep!lepsy12_Audit",
            first_name="Super",
            surname="User",
            role=RCPCH_AUDIT_TEAM,
            is_rcpch_audit_team_member=True,
        )

        assert superuser.is_superuser is True
        assert superuser.is_rcpch_staff is True
        assert superuser.is_rcpch_audit_team_member is True

    def test_create_superuser_defaults_national_view_preference(
        self, seed_groups_fixture
    ):
        """Superusers default to the national view scope (2).

        The intended ``setdefault("view_preference", 2)`` in create_superuser
        was dead code: it was shadowed by an earlier ``setdefault(0)`` in the
        same method, and create_user then clobbered it with an unconditional
        ``user.view_preference = 0`` anyway - so superusers always landed on
        organisation scope despite the "national scope" intent.
        """
        user_model = get_user_model()

        superuser = user_model.objects.create_superuser(
            email="national_superuser@example.com",
            password="Ep!lepsy12_Audit",
            first_name="National",
            surname="Superuser",
            role=RCPCH_AUDIT_TEAM,
            is_rcpch_audit_team_member=True,
        )

        superuser.refresh_from_db()
        assert superuser.view_preference == 2

    def test_create_user_still_defaults_organisation_view_preference(
        self, seed_groups_fixture, GOSH
    ):
        """create_user must keep defaulting to organisation scope (0) when no
        view_preference is passed - only an explicit preference is honoured.
        """
        user_model = get_user_model()

        user = user_model.objects.create_user(
            email="org_default@example.com",
            password="Ep!lepsy12_Audit",
            first_name="Org",
            surname="User",
            role=AUDIT_CENTRE_ADMINISTRATOR,
            organisation_employer=GOSH,
        )

        user.refresh_from_db()
        assert user.view_preference == 0
