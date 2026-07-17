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

# RCPCH imports
from epilepsy12.admin import Epilepsy12UserAdmin
from epilepsy12.constants.user_types import RCPCH_AUDIT_TEAM
from epilepsy12.models import Epilepsy12User


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
