"""
Tests that national access comes from the RCPCH Audit Team role's group
permissions, and that a system check catches an audit team group the seeder
has not brought up to date.
"""

from types import SimpleNamespace

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied

from epilepsy12.checks import check_rcpch_audit_team_permissions
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_TEAM,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
)
from epilepsy12.decorator import _user_may_view_this_organisation
from epilepsy12.general_functions.audit_period_permissions import _is_rcpch_user
from epilepsy12.models import Organisation


def _run_check():
    return check_rcpch_audit_team_permissions(None, databases=["default"])


def _audit_team_group():
    return Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)


# ---------------------------------------------------------------------------
# System check
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_check_passes_when_group_is_seeded():
    assert _run_check() == []


@pytest.mark.django_db
def test_check_errors_when_group_is_missing_a_permission():
    view_banner = Permission.objects.get(codename="view_banner")
    _audit_team_group().permissions.remove(view_banner)

    errors = _run_check()

    assert len(errors) == 1
    assert errors[0].id == "epilepsy12.E001"
    assert "epilepsy12.view_banner" in errors[0].msg
    assert "seed_groups_and_permissions" in errors[0].hint


@pytest.mark.django_db
def test_check_skipped_without_databases():
    """Plain ``manage.py check`` and runserver don't run database checks."""
    _audit_team_group().permissions.clear()

    assert check_rcpch_audit_team_permissions(None, databases=None) == []


@pytest.mark.django_db
def test_check_skipped_before_group_exists():
    """A fresh database has no groups until the seeder runs."""
    _audit_team_group().delete()

    assert _run_check() == []


@pytest.mark.django_db
def test_check_ignores_permission_not_created_yet():
    """``migrate`` runs the check before applying migrations, so a permission
    added by a pending migration must not block the deploy that adds it."""
    Permission.objects.filter(codename="view_banner").delete()

    assert _run_check() == []


# ---------------------------------------------------------------------------
# Access comes from the role's group
# ---------------------------------------------------------------------------


@pytest.fixture
def other_trust_organisation():
    """An organisation outside GOSH's trust, which the factory employs users at."""
    return Organisation.objects.get(ods_code="RGT01", trust__ods_code="RGT")


@pytest.mark.django_db
def test_trust_role_has_no_national_access(
    e12_user_factory, other_trust_organisation
):
    clinician = e12_user_factory(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        groups=[Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)],
    )

    assert _is_rcpch_user(clinician) is False
    with pytest.raises(PermissionDenied):
        _user_may_view_this_organisation(
            SimpleNamespace(user=clinician),
            {"organisation_id": other_trust_organisation.pk},
        )


@pytest.mark.django_db
def test_audit_team_role_grants_national_access(
    e12_user_factory, other_trust_organisation
):
    audit_team_member = e12_user_factory(
        role=RCPCH_AUDIT_TEAM,
        groups=[_audit_team_group()],
    )

    assert _is_rcpch_user(audit_team_member) is True
    # does not raise
    _user_may_view_this_organisation(
        SimpleNamespace(user=audit_team_member),
        {"organisation_id": other_trust_organisation.pk},
    )


@pytest.mark.django_db
def test_superuser_has_national_access_without_group(
    e12_user_factory, other_trust_organisation
):
    superuser = e12_user_factory(role=RCPCH_AUDIT_TEAM, is_superuser=True)

    assert _is_rcpch_user(superuser) is True
    _user_may_view_this_organisation(
        SimpleNamespace(user=superuser),
        {"organisation_id": other_trust_organisation.pk},
    )
