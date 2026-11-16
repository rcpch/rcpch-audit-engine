"""
Tests for Epilepsy12UserAdmin.save_model.

Changing a user's role in the Django admin keeps the RCPCH flags and the
user's group in step with the new role (Phase 0 of the
is_rcpch_audit_team_member / is_rcpch_staff retirement plan: role is the
source of truth for national access). Flags edited *without* a role change
are preserved, so superusers can triage audit_rcpch_user_flags findings
here.
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
def test_admin_role_change_syncs_flags_and_group():
    """
    Promoting a Lead Clinician to the RCPCH Audit Team role in the admin sets
    both flags and moves the user into the RCPCH audit team group.
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    user = E12UserFactory(
        email="temp_admin_promotion_candidate@test.com",
        first_name="TEMP_ADMIN_PROMOTION_CANDIDATE",
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    user.role = RCPCH_AUDIT_TEAM
    form = SimpleNamespace(changed_data=["role"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.role == RCPCH_AUDIT_TEAM
    assert user.is_rcpch_audit_team_member == True
    assert user.is_rcpch_staff == True
    assert list(user.groups.values_list("name", flat=True)) == [
        EPILEPSY12_AUDIT_TEAM_FULL_ACCESS
    ]


@pytest.mark.django_db
def test_admin_role_change_can_demote_and_clear_flags():
    """
    Demoting an RCPCH Audit Team member to an audit centre role in the admin
    clears both flags and moves the user back into the role's group.
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    user = E12UserFactory(
        email="temp_admin_demotion_candidate@test.com",
        first_name="TEMP_ADMIN_DEMOTION_CANDIDATE",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        groups=[Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)],
    )

    user.role = AUDIT_CENTRE_LEAD_CLINICIAN
    form = SimpleNamespace(changed_data=["role"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.role == AUDIT_CENTRE_LEAD_CLINICIAN
    assert user.is_rcpch_audit_team_member == False
    assert user.is_rcpch_staff == False
    assert list(user.groups.values_list("name", flat=True)) == [
        TRUST_AUDIT_TEAM_FULL_ACCESS
    ]


@pytest.mark.django_db
def test_admin_flag_change_without_role_change_is_preserved():
    """
    A flag edited in the admin without a role change is kept, so superusers
    can triage audit_rcpch_user_flags findings here (e.g. accept the loss of
    national access for a flag_without_role user by clearing their flag but
    keeping their role).
    """
    user_admin = Epilepsy12UserAdmin(Epilepsy12User, AdminSite())

    # a flag_without_role finding: Lead Clinician with the audit team flag
    user = E12UserFactory(
        email="temp_admin_triage_candidate@test.com",
        first_name="TEMP_ADMIN_TRIAGE_CANDIDATE",
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=False,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    # superuser clears the flag, role untouched
    user.is_rcpch_audit_team_member = False
    form = SimpleNamespace(changed_data=["is_rcpch_audit_team_member"])

    request = RequestFactory().get("/")
    request.user = user  # SimpleHistoryAdmin records request.user as the history user
    user_admin.save_model(request, user, form, change=True)

    user.refresh_from_db()

    assert user.role == AUDIT_CENTRE_LEAD_CLINICIAN
    assert user.is_rcpch_audit_team_member == False
    assert user.is_rcpch_staff == False
    assert list(user.groups.values_list("name", flat=True)) == [
        TRUST_AUDIT_TEAM_FULL_ACCESS
    ]
