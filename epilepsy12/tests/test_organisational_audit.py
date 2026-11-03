import csv
import io

import pytest

from epilepsy12.models import (
    Organisation,
    OrganisationalAuditSubmission,
    OrganisationalAuditSubmissionPeriod,
)
from epilepsy12.organisational_audit import export_submission_period_as_csv


@pytest.mark.django_db
def test_organisational_audit_export_2026_multiselect_columns(
    seed_groups_fixture,
    seed_users_fixture,
):
    """These columns don't have a corresponding mapping in MULTISELECT_FIELD_MAPPINGS
    as the questions were added on the new platform and had no corresponding entry in
    the old one. We "widen" the multiselect field into separate columns for each option
    for consistency with how the old platform worked.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2026,
        is_open=False,
    )

    OrganisationalAuditSubmission.objects.create(
        submission_period=submission_period,
        trust=GOSH.trust,
        local_health_board=None,
        # a multiselect field takes an iterable of the choice values, here
        # Ready Steady Go (1), EpiTRAQ (3) and A local tool (4, free text)
        S06WhichStructuredResourcesToSupportTransition=[1, 3 ,4],
        S06WhichStructuredResourcesToSupportTransitionOtherDetails="a tool"
    )

    csv_data = export_submission_period_as_csv(submission_period)

    assert csv_data, "Export should produce non-empty CSV"
    assert isinstance(csv_data, str), "Export should return a string"

    rows = list(csv.DictReader(io.StringIO(csv_data)))
    assert len(rows) == 1

    row = rows[0]
    assert row["S06WhichStructuredResourcesToSupportTransition_1"] == "1"
    assert row["S06WhichStructuredResourcesToSupportTransition_2"] == "2"
    assert row["S06WhichStructuredResourcesToSupportTransition_3"] == "1"
    assert row["S06WhichStructuredResourcesToSupportTransition_4"] == "1"
    assert row["S06WhichStructuredResourcesToSupportTransitionOtherDetails"] == "a tool"
