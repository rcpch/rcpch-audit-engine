"""
Tests for Epilepsy12UserAdmin.save_model.

Changing a user's role in the Django admin moves them into the new role's
group: role is the source of truth for a user's permissions, including
national access. Edits that don't change the role leave groups alone.
"""

from types import SimpleNamespace

import pytest

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from django.test import RequestFactory

from epilepsy12.admin import Epilepsy12UserAdmin
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_TEAM,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
)
from epilepsy12.models import Epilepsy12User
from epilepsy12.tests.factories import E12UserFactory


@pytest.mark.django_db
def test_admin_role_change_syncs_group():
    """
    Promoting a Lead Clinician to the RCPCH Audit Team role in the admin moves
    the user into the RCPCH audit team group.
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    user = E12UserFactory(
        email="temp_admin_promotion_candidate@test.com",
        first_name="TEMP_ADMIN_PROMOTION_CANDIDATE",
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    user.role = RCPCH_AUDIT_TEAM
    form = SimpleNamespace(changed_data=["role"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.role == RCPCH_AUDIT_TEAM
    assert list(user.groups.values_list("name", flat=True)) == [
        EPILEPSY12_AUDIT_TEAM_FULL_ACCESS
    ]


@pytest.mark.django_db
def test_admin_role_change_can_demote():
    """
    Demoting an RCPCH Audit Team member to an audit centre role in the admin
    moves the user back into the role's group.
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    user = E12UserFactory(
        email="temp_admin_demotion_candidate@test.com",
        first_name="TEMP_ADMIN_DEMOTION_CANDIDATE",
        role=RCPCH_AUDIT_TEAM,
        groups=[Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)],
    )

    user.role = AUDIT_CENTRE_LEAD_CLINICIAN
    form = SimpleNamespace(changed_data=["role"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.role == AUDIT_CENTRE_LEAD_CLINICIAN
    assert list(user.groups.values_list("name", flat=True)) == [
        TRUST_AUDIT_TEAM_FULL_ACCESS
    ]


@pytest.mark.django_db
def test_admin_edit_without_role_change_leaves_groups_alone():
    """
    Editing a field other than role in the admin doesn't touch groups, so a
    group a superuser set by hand is kept.
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    user = E12UserFactory(
        email="temp_admin_edit_candidate@test.com",
        first_name="TEMP_ADMIN_EDIT_CANDIDATE",
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    user.surname = "Edited"
    form = SimpleNamespace(changed_data=["surname"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.surname == "Edited"
    assert list(user.groups.values_list("name", flat=True)) == [
        TRUST_AUDIT_TEAM_FULL_ACCESS
    ]


def test_retired_user_flag_history_admin_is_read_only():
    """The archive of the retired RCPCH flags can be viewed but never edited."""
    from epilepsy12.admin import RetiredUserFlagHistoryAdmin
    from epilepsy12.models import RetiredUserFlagHistory

    archive_admin = RetiredUserFlagHistoryAdmin(RetiredUserFlagHistory, AdminSite())
    request = RequestFactory().get("/")

    assert archive_admin.has_add_permission(request) is False
    assert archive_admin.has_change_permission(request) is False
    assert archive_admin.has_delete_permission(request) is False
