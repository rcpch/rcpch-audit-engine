"""
Tests for the ``sync_nhs_organisations`` management command.

These tests mock the API client functions so no network access is required.
The dry-run test verifies that the command calls the API list functions and
reports counts without writing to the database. The live-sync test verifies
that the command calls ``sync_current_state()`` and reports the result.
"""

from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from epilepsy12.general_functions import nhs_organisations
from epilepsy12.management.commands import sync_nhs_organisations as cmd


@pytest.mark.django_db
def test_sync_nhs_organisations_dry_run_reports_counts_without_writing():
    """--dry-run calls the API list functions and reports counts, but does
    not call any sync (upsert) function."""
    with patch.object(
        nhs_organisations, "list_trusts", return_value=[{"ods_code": "RGT"}]
    ), patch.object(
        nhs_organisations,
        "list_local_health_boards",
        return_value=[{"ods_code": "7A3"}],
    ), patch.object(
        nhs_organisations,
        "list_integrated_care_boards",
        return_value=[{"ods_code": "QUE"}],
    ), patch.object(
        nhs_organisations,
        "list_nhs_england_regions",
        return_value=[{"region_code": "Y61"}],
    ), patch.object(
        nhs_organisations,
        "list_countries",
        return_value=[{"boundary_identifier": "E92000001"}],
    ), patch.object(
        nhs_organisations,
        "list_openuk_networks",
        return_value=[{"boundary_identifier": "EPEN"}],
    ), patch.object(
        nhs_organisations,
        "list_organisations",
        return_value=[{"ods_code": "RGT01"}],
    ), patch.object(cmd, "sync_current_state") as mock_sync:
        out = StringIO()
        call_command("sync_nhs_organisations", "--dry-run", stdout=out)

    output = out.getvalue()
    assert "Dry-run mode" in output
    assert "Trusts: 1 from API" in output
    assert "Local Health Boards: 1 from API" in output
    assert "Integrated Care Boards: 1 from API" in output
    assert "NHS England Regions: 1 from API" in output
    assert "Countries: 1 from API" in output
    assert "OPEN UK Networks: 1 from API" in output
    assert "Organisations: 1 from API" in output
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
    with patch.object(cmd, "sync_current_state", return_value=fake_result):
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
    with patch.object(cmd, "sync_trusts", return_value=fake_trusts) as mock_sync_trusts, patch.object(
        cmd, "sync_current_state"
    ) as mock_sync_all:
        out = StringIO()
        call_command("sync_nhs_organisations", "--only", "trusts", stdout=out)

    output = out.getvalue()
    assert "Syncing only: trusts" in output
    assert "Synced 1 trusts" in output
    mock_sync_trusts.assert_called_once_with()
    mock_sync_all.assert_not_called()
