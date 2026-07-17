"""
Tests that Epilepsy12User.is_staff (Django admin access) is always kept in
sync with is_superuser - there is no separate flag to set to gain access to
the Django admin.
"""

# Standard imports
import pytest

# Third party imports
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse

# RCPCH imports
from epilepsy12.admin import Epilepsy12UserAdmin
from epilepsy12.constants.user_types import RCPCH_AUDIT_TEAM
from epilepsy12.models import Epilepsy12User
from epilepsy12.tests.UserDataClasses import test_user_audit_centre_lead_clinician_data
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
def test_is_staff_mirrors_is_superuser_on_create(e12_user_factory):
    # is_staff explicitly set "wrong" - save() should always override it
    superuser = e12_user_factory(
        is_superuser=True,
        is_staff=False,
        role=RCPCH_AUDIT_TEAM,
    )
    assert superuser.is_staff is True

    non_superuser = e12_user_factory(
        is_superuser=False,
        is_staff=True,
        role=RCPCH_AUDIT_TEAM,
    )
    assert non_superuser.is_staff is False


@pytest.mark.django_db
def test_is_staff_flips_when_is_superuser_toggled(e12_user_factory):
    user = e12_user_factory(is_superuser=False, role=RCPCH_AUDIT_TEAM)
    assert user.is_staff is False

    # promotion
    user.is_superuser = True
    user.save()
    assert user.is_staff is True

    # demotion
    user.is_superuser = False
    user.save()
    assert user.is_staff is False


@pytest.mark.django_db
def test_create_superuser_sets_is_staff_without_is_staff_kwarg(GOSH):
    user_model = get_user_model()

    superuser = user_model.objects.create_superuser(
        email="new_superuser@example.com",
        password="Ep!lepsy12_Audit",
        first_name="Super",
        surname="User",
        role=RCPCH_AUDIT_TEAM,
        organisation_employer=GOSH,
    )

    assert superuser.is_superuser is True
    assert superuser.is_staff is True


@pytest.mark.django_db
def test_non_superuser_cannot_access_django_admin(
    client, seed_groups_fixture, seed_users_fixture
):
    """
    Defensive test for the removal of Epilepsy12UserAdmin.get_form()'s old
    per-field exclusion of is_superuser: that was only needed because a
    non-superuser could otherwise reach the admin's user form at all. Now
    that is_staff is fully derived from is_superuser, a non-superuser
    should never pass the admin site's has_permission() check in the first
    place, so they have no route to reach that form and grant themselves
    (or anyone else) is_superuser via /admin/.
    """
    non_superuser = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )
    assert non_superuser.is_superuser is False
    assert non_superuser.is_staff is False

    client.force_login(non_superuser)
    twofactor_signin(client, non_superuser)

    response = client.get(reverse("admin:index"))

    assert admin.site.has_permission(response.wsgi_request) is False


@pytest.mark.django_db
def test_superuser_can_access_django_admin(e12_user_factory, client):
    """Control case for test_non_superuser_cannot_access_django_admin."""
    superuser = e12_user_factory(is_superuser=True, role=RCPCH_AUDIT_TEAM)
    # E12UserFactory's groups post_generation hook sets a password in memory
    # but only persists it when a `groups=` kwarg is passed; reload from the
    # DB so force_login()'s session auth hash matches what's actually stored.
    superuser.refresh_from_db()

    client.force_login(superuser)
    twofactor_signin(client, superuser)

    response = client.get(reverse("admin:index"))

    assert admin.site.has_permission(response.wsgi_request) is True


def test_epilepsy12_user_admin_does_not_expose_is_staff_field():
    """
    is_staff is derived automatically from is_superuser, so it should no
    longer be a directly editable (or even visible) field in the Django
    admin's own user management screens.
    """
    admin_instance = Epilepsy12UserAdmin(Epilepsy12User, admin.site)

    fieldset_fields = [
        field for _, opts in admin_instance.fieldsets for field in opts["fields"]
    ]
    add_fieldset_fields = [
        field for _, opts in admin_instance.add_fieldsets for field in opts["fields"]
    ]

    assert "is_staff" not in fieldset_fields
    assert "is_staff" not in add_fieldset_fields
    assert "is_staff" not in admin_instance.list_display
