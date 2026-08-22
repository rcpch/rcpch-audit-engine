"""
Tests for the ``sync_nhs_organisations`` management command.

These tests mock the API client functions so no network access is required.
The dry-run test verifies that the command produces a field-level diff
report without writing to the database. The live-sync test verifies that
the command calls ``sync_current_state()`` and reports the result.
"""

from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from epilepsy12.management.commands import sync_nhs_organisations as cmd


@pytest.mark.django_db
def test_sync_nhs_organisations_dry_run_reports_diff_without_writing():
    """--dry-run compares API state against the local DB and reports
    new/changed/unchanged/local-only, but does not call any sync function."""
    # The API returns one trust that doesn't exist locally (new) and one
    # that does exist but with a different name (changed).
    api_trusts = [
        {"ods_code": "RXX", "name": "NEW TRUST", "active": True, "published_at": ""},
        {"ods_code": "RGT", "name": "UPDATED NAME", "active": True, "published_at": ""},
    ]

    # Pre-create the RGT trust with a different name so it shows as "changed"
    from epilepsy12.models import Trust

    Trust.objects.get_or_create(
        ods_code="RGT", defaults={"name": "OLD NAME", "active": True}
    )

    with patch.object(cmd, "sync_current_state") as mock_sync, patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_trusts",
        return_value=api_trusts,
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_local_health_boards",
        return_value=[],
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_integrated_care_boards",
        return_value=[],
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_nhs_england_regions",
        return_value=[],
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_countries",
        return_value=[],
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_openuk_networks",
        return_value=[],
    ), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.list_organisations",
        return_value=[],
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", "--dry-run", stdout=out)

    output = out.getvalue()
    assert "Dry-run mode" in output
    assert "Comparing API state" in output
    # RXX is new
    assert "RXX" in output
    assert "NEW TRUST" in output
    # RGT is changed (name differs)
    assert "RGT" in output
    assert "name:" in output
    assert "UPDATED NAME" in output
    # No changes written
    assert "No changes written" in output
    # sync_current_state must not be called in dry-run mode
    mock_sync.assert_not_called()


@pytest.mark.django_db
def test_sync_nhs_organisations_live_sync_calls_sync_current_state():
    """Without --dry-run, the command calls sync_current_state() and reports
    the returned counts."""
    fake_result = {
        "trusts": 150,
        "local_health_boards": 7,
        "integrated_care_boards": 42,
        "nhs_england_regions": 7,
        "countries": 4,
        "openuk_networks": 12,
        "organisations": 200,
    }
    fake_safety = {
        "blocked": False,
        "block_reason": "",
        "requires_confirm": False,
        "total_registrations": 0,
        "total_registrations_in_flight": 0,
        "total_cases": 0,
        "high_impact_changes": [],
    }
    with patch.object(cmd, "sync_current_state", return_value=fake_result), patch(
        "epilepsy12.general_functions.nhs_organisations_sync.pre_sync_safety_check",
        return_value=fake_safety,
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", stdout=out)

    output = out.getvalue()
    assert "Syncing all entities" in output
    assert "Trusts: 150" in output
    assert "Local Health Boards: 7" in output
    assert "Integrated Care Boards: 42" in output
    assert "Nhs England Regions: 7" in output
    assert "Countries: 4" in output
    assert "Openuk Networks: 12" in output
    assert "Organisations: 200" in output
    assert "Sync complete" in output


@pytest.mark.django_db
def test_sync_nhs_organisations_only_trusts():
    """--only trusts syncs only trusts, not all entities."""
    fake_trusts = {"RGT": "trust_obj"}
    fake_safety = {
        "blocked": False,
        "block_reason": "",
        "requires_confirm": False,
        "total_registrations": 0,
        "total_registrations_in_flight": 0,
        "total_cases": 0,
        "high_impact_changes": [],
    }
    with patch.object(cmd, "sync_trusts", return_value=fake_trusts) as mock_sync_trusts, patch.object(
        cmd, "sync_current_state"
    ) as mock_sync_all, patch(
        "epilepsy12.general_functions.nhs_organisations_sync.pre_sync_safety_check",
        return_value=fake_safety,
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", "--only", "trusts", stdout=out)

    output = out.getvalue()
    assert "Syncing only: trusts" in output
    assert "Synced 1 trusts" in output
    mock_sync_trusts.assert_called_once_with()
    mock_sync_all.assert_not_called()


@pytest.mark.django_db
def test_sync_nhs_organisations_blocks_when_safety_check_blocks():
    """When the safety check returns blocked=True, the command prints the
    block reason and does not call sync_current_state."""
    fake_safety = {
        "blocked": True,
        "block_reason": "in-flight periods have no approved memberships",
        "requires_confirm": False,
        "total_registrations": 0,
        "total_registrations_in_flight": 0,
        "total_cases": 0,
        "high_impact_changes": [],
    }
    with patch.object(cmd, "sync_current_state") as mock_sync, patch(
        "epilepsy12.general_functions.nhs_organisations_sync.pre_sync_safety_check",
        return_value=fake_safety,
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", stdout=out)

    output = out.getvalue()
    assert "Sync blocked" in output
    assert "in-flight periods" in output
    assert "sync_audit_period_organisations" in output
    mock_sync.assert_not_called()


@pytest.mark.django_db
def test_sync_nhs_organisations_requires_confirm_without_flag():
    """When requires_confirm=True and --confirm is not passed, the command
    prints the exposure summary and does not call sync_current_state."""
    fake_safety = {
        "blocked": False,
        "block_reason": "",
        "requires_confirm": True,
        "total_registrations": 42,
        "total_registrations_in_flight": 10,
        "total_cases": 50,
        "high_impact_changes": [
            ("organisations", "RP401", "trust: RP4 -> RJZ"),
        ],
    }
    with patch.object(cmd, "sync_current_state") as mock_sync, patch(
        "epilepsy12.general_functions.nhs_organisations_sync.pre_sync_safety_check",
        return_value=fake_safety,
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", stdout=out)

    output = out.getvalue()
    assert "would affect registrations or cases" in output
    assert "42" in output
    assert "10" in output
    assert "50" in output
    assert "RP401" in output
    assert "trust: RP4 -> RJZ" in output
    assert "Sync complete" not in output
    mock_sync.assert_not_called()


@pytest.mark.django_db
def test_sync_nhs_organisations_proceeds_with_confirm():
    """When requires_confirm=True and --confirm is passed, the command
    prints the confirmed impact and proceeds to call sync_current_state."""
    fake_result = {"trusts": 1, "local_health_boards": 0, "integrated_care_boards": 0,
                   "nhs_england_regions": 0, "countries": 0, "openuk_networks": 0,
                   "organisations": 1}
    fake_safety = {
        "blocked": False,
        "block_reason": "",
        "requires_confirm": True,
        "total_registrations": 42,
        "total_registrations_in_flight": 10,
        "total_cases": 50,
        "high_impact_changes": [
            ("organisations", "RP401", "trust: RP4 -> RJZ"),
        ],
    }
    with patch.object(cmd, "sync_current_state", return_value=fake_result) as mock_sync, patch(
        "epilepsy12.general_functions.nhs_organisations_sync.pre_sync_safety_check",
        return_value=fake_safety,
    ):
        out = StringIO()
        call_command("sync_nhs_organisations", "--confirm", stdout=out)

    output = out.getvalue()
    assert "Proceeding with confirmed impact" in output
    assert "42" in output
    assert "Sync complete" in output
    mock_sync.assert_called_once_with()
