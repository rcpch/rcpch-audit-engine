"""
Tests for ``AuditPeriod.objects.for_first_paediatric_assessment_date()``.

This is the single function the whole cohort-assignment now hinges on: it is
called by ``Registration.save()`` to resolve a registration's ``audit_period``
(and hence ``cohort``) from the first paediatric assessment (FPA) date.

The point of these tests is to lock in the cohort 8 -> 9 transition, where the
audit team moved recruitment to align with the calendar year and gave cohort 8
an extra transition month (recruitment ending 2025-12-31). This is exactly where
the new DB-driven mapping deliberately diverges from the old arithmetic
(``year - 2016``) logic it replaced:

    * FPA in Dec 2025  -> cohort 8 here   (old arithmetic gave cohort 9)
    * FPA in Dec 2026  -> cohort 9 here   (old arithmetic gave cohort 10)

The AuditPeriod rows for cohorts 4-9 are seeded into the test DB by the
``seed_audit_periods_fixture`` (session-scoped, autouse) in conftest.py, so a
plain ``@pytest.mark.django_db`` test can query the mapping directly.
"""

from datetime import date, timedelta

import pytest

from epilepsy12.constants.audit_period_extension_reasons import (
    AUDIT_PERIOD_EXTENSION_REASONS,
)
from epilepsy12.models import AuditPeriod, AuditPeriodExtension


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fpa_date, expected_cohort",
    [
        # --- cohort 4 lower bound ---
        (date(2020, 12, 1), 4),   # first day cohort 4 opens
        (date(2021, 11, 30), 4),  # last day of cohort 4
        (date(2021, 12, 1), 5),   # first day of cohort 5
        # --- cohort 7 / 8 boundary (unaffected by the transition) ---
        (date(2024, 11, 30), 7),  # last day of cohort 7
        (date(2024, 12, 1), 8),   # first day of cohort 8
        # --- cohort 8's extra transition month ---
        (date(2025, 11, 30), 8),  # old arithmetic also gave 8
        (date(2025, 12, 1), 8),   # DIVERGENCE: old arithmetic gave 9
        (date(2025, 12, 31), 8),  # DIVERGENCE: last day of cohort 8 (old gave 9)
        # --- cohort 9 == the 2026 calendar year ---
        (date(2026, 1, 1), 9),    # first day of cohort 9
        (date(2026, 11, 30), 9),
        (date(2026, 12, 1), 9),   # DIVERGENCE: old arithmetic gave 10
        (date(2026, 12, 31), 9),  # DIVERGENCE: last day of cohort 9 (old gave 10)
    ],
)
def test_for_fpa_date_maps_to_expected_cohort(fpa_date, expected_cohort):
    period = AuditPeriod.objects.for_first_paediatric_assessment_date(fpa_date)

    assert period is not None, (
        f"Expected FPA date {fpa_date} to resolve to cohort {expected_cohort}, "
        f"but no AuditPeriod matched."
    )
    assert period.cohort_number == expected_cohort, (
        f"FPA date {fpa_date} resolved to cohort {period.cohort_number}, "
        f"expected {expected_cohort}."
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fpa_date",
    [
        date(2020, 11, 30),  # day before cohort 4 opens - too early
        date(2027, 1, 1),    # beyond the last seeded period (cohort 9 ends 2026-12-31)
    ],
    ids=["before-cohort-4", "after-last-seeded-cohort"],
)
def test_for_fpa_date_returns_none_outside_seeded_periods(fpa_date):
    """Dates not covered by any seeded AuditPeriod return None (never a guess).

    The 'after-last-seeded-cohort' case also documents the operational
    requirement to seed cohort 10 before FPA dates from 2027 can be registered.
    """
    assert AuditPeriod.objects.for_first_paediatric_assessment_date(fpa_date) is None


@pytest.mark.django_db
@pytest.mark.parametrize("reason_code, _", AUDIT_PERIOD_EXTENSION_REASONS)
def test_extension_reason_stores_coded_value(GOSH, reason_code, _):
    """Each coded reason can be stored on the extension and round-trips as an int."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    extension = AuditPeriodExtension.objects.create(
        audit_period=audit_period,
        organisation=GOSH,
        extended_submission_date=audit_period.submission_deadline + timedelta(days=28),
        reason=reason_code,
    )

    extension.refresh_from_db()

    assert extension.reason == reason_code
    assert isinstance(extension.reason, int)


@pytest.mark.django_db
@pytest.mark.parametrize("reason_code, expected_label", AUDIT_PERIOD_EXTENSION_REASONS)
def test_extension_reason_display_label(GOSH, reason_code, expected_label):
    """get_reason_display() returns the human-readable label for each coded reason."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    extension = AuditPeriodExtension.objects.create(
        audit_period=audit_period,
        organisation=GOSH,
        extended_submission_date=audit_period.submission_deadline + timedelta(days=28),
        reason=reason_code,
    )

    assert extension.get_reason_display() == expected_label
