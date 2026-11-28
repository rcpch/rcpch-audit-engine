"""
Tests that the role and permission flags of a user are recorded in
VisitActivity: as they stand when the user is created (CREATED_USER_RECORD),
and when they change afterwards.
"""

import pytest

from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)
from epilepsy12.models import VisitActivity


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role, role_display, is_active, is_superuser",
    [
        (AUDIT_CENTRE_CLINICIAN, "Clinician", True, False),
        (RCPCH_AUDIT_TEAM, "RCPCH Audit Team", False, True),
    ],
)
def test_user_creation_logs_role_and_flags(
    e12_user_factory, role, role_display, is_active, is_superuser
):
    user = e12_user_factory(
        role=role, is_active=is_active, is_superuser=is_superuser
    )

    creation = VisitActivity.objects.get(
        epilepsy12user=user, activity=VisitActivity.CREATED_USER_RECORD
    )

    assert f"role: '{role}' ({role_display})" in creation.details
    assert f"is_active: '{is_active}'" in creation.details
    assert f"is_superuser: '{is_superuser}'" in creation.details


@pytest.mark.django_db
def test_superuser_change_is_logged_as_admin_flag_change(e12_user_factory):
    user = e12_user_factory(role=RCPCH_AUDIT_TEAM, is_superuser=False)

    user.is_superuser = True
    user.save()

    change = VisitActivity.objects.get(
        epilepsy12user=user, activity=VisitActivity.CHANGED_ADMIN_FLAG
    )
    assert "is_superuser: 'False' → 'True'" in change.details


@pytest.mark.django_db
def test_role_change_is_logged(e12_user_factory):
    user = e12_user_factory(role=AUDIT_CENTRE_CLINICIAN)

    user.role = RCPCH_AUDIT_TEAM
    user.save()

    change = VisitActivity.objects.get(
        epilepsy12user=user, activity=VisitActivity.CHANGED_USER_ROLE
    )
    assert f"role: '{AUDIT_CENTRE_CLINICIAN}' → '{RCPCH_AUDIT_TEAM}'" in change.details
