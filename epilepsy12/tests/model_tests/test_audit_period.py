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
from django.core.exceptions import ValidationError

from epilepsy12.constants.audit_period_extension_reasons import (
    AUDIT_PERIOD_EXTENSION_REASONS,
)
from epilepsy12.models import AuditPeriod, AuditPeriodExtension, Epilepsy12User

# Cohort 6 seeded dates (see epilepsy12/constants/audit_period_dates.py):
#   recruitment    2022-12-01 -> 2023-11-30
#   data collect   2023-12-01 -> 2024-11-30
#   grace          2024-12-01 -> 2025-01-14
COHORT_6_SUBMISSION_DEADLINE = date(2025, 1, 14)
COHORT_6_DATA_COLLECTION = date(2024, 6, 1)   # inside data collection window
COHORT_6_GRACE = date(2025, 1, 6)             # inside grace window
COHORT_6_RECRUITING = date(2023, 6, 1)        # inside recruitment window


def _extension(audit_period, organisation, days=28, reason=0):
    return AuditPeriodExtension.objects.create(
        audit_period=audit_period,
        organisation=organisation,
        extended_submission_date=audit_period.submission_deadline + timedelta(days=days),
        reason=reason,
    )


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


# ---------------------------------------------------------------------------
# as_cohort_card_dict
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_card_dict_without_organisation_shows_audit_wide_deadline():
    """With no organisation the card shows the audit-wide deadline and no badge."""
    audit_period = AuditPeriod.objects.by_cohort(6)

    card = audit_period.as_cohort_card_dict(today=COHORT_6_DATA_COLLECTION)

    assert card["cohort"] == 6
    assert card["audit_period_id"] == audit_period.pk
    assert card["submission_date"] == COHORT_6_SUBMISSION_DEADLINE
    assert card["extended_submission_date"] is None


@pytest.mark.django_db
def test_card_dict_days_remaining_is_inclusive_and_audit_wide_without_organisation():
    """days_remaining counts inclusively up to the audit-wide deadline."""
    audit_period = AuditPeriod.objects.by_cohort(6)

    card = audit_period.as_cohort_card_dict(today=COHORT_6_GRACE)

    expected_days = (COHORT_6_SUBMISSION_DEADLINE - COHORT_6_GRACE).days + 1
    assert card["days_remaining"] == expected_days


@pytest.mark.django_db
def test_card_dict_with_extension_shows_extended_badge_and_counts_to_extended_date(GOSH):
    """An org with an extension gets the badge date and a countdown to the extension."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    extension = _extension(audit_period, GOSH, days=28)

    card = audit_period.as_cohort_card_dict(
        today=COHORT_6_GRACE, organisation=GOSH
    )

    # original audit-wide deadline stays displayed
    assert card["submission_date"] == COHORT_6_SUBMISSION_DEADLINE
    # badge shows the extension
    assert card["extended_submission_date"] == extension.extended_submission_date
    # countdown honours the extension
    expected_days = (extension.extended_submission_date - COHORT_6_GRACE).days + 1
    assert card["days_remaining"] == expected_days


@pytest.mark.django_db
def test_card_dict_extension_is_organisation_specific(GOSH, ADDENBROOKES):
    """An extension held by one organisation must not appear on another's card."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    _extension(audit_period, GOSH, days=28)

    gosh_card = audit_period.as_cohort_card_dict(
        today=COHORT_6_GRACE, organisation=GOSH
    )
    addenbrookes_card = audit_period.as_cohort_card_dict(
        today=COHORT_6_GRACE, organisation=ADDENBROOKES
    )

    assert gosh_card["extended_submission_date"] is not None
    assert addenbrookes_card["extended_submission_date"] is None
    assert addenbrookes_card["submission_date"] == COHORT_6_SUBMISSION_DEADLINE


@pytest.mark.django_db
@pytest.mark.parametrize(
    "today, expected_eligible",
    [
        (COHORT_6_DATA_COLLECTION, True),   # submitting cohort
        (COHORT_6_GRACE, True),             # grace cohort
        (COHORT_6_RECRUITING, False),       # still recruiting
        (date(2025, 1, 15), False),         # after audit-wide deadline
    ],
    ids=["submitting", "grace", "recruiting", "complete"],
)
def test_card_dict_extension_eligibility(today, expected_eligible):
    """Extension button only offered for the submitting and grace cohorts."""
    audit_period = AuditPeriod.objects.by_cohort(6)

    card = audit_period.as_cohort_card_dict(today=today)

    assert card["is_extension_eligible"] is expected_eligible


# ---------------------------------------------------------------------------
# cohort_summary
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cohort_summary_threads_organisation_into_card_dicts(GOSH, ADDENBROOKES):
    """The submitting cohort card is individualised for the given organisation."""
    submitting = AuditPeriod.objects.currently_submitting()
    assert submitting is not None, "No seeded cohort is currently submitting."

    extension = _extension(submitting, GOSH, days=28)

    summary = AuditPeriod.objects.cohort_summary(organisation=GOSH)
    card = summary["submitting_cohort_dates"]

    assert card["extended_submission_date"] == extension.extended_submission_date

    # a different organisation sees no badge
    summary_other = AuditPeriod.objects.cohort_summary(organisation=ADDENBROOKES)
    assert summary_other["submitting_cohort_dates"]["extended_submission_date"] is None


@pytest.mark.django_db
def test_cohort_summary_days_remaining_honours_extension(GOSH):
    """The standalone days_remaining key also counts to the extended deadline."""
    submitting = AuditPeriod.objects.currently_submitting()
    assert submitting is not None, "No seeded cohort is currently submitting."

    extension = _extension(submitting, GOSH, days=28)

    summary = AuditPeriod.objects.cohort_summary(organisation=GOSH)
    expected_days = (extension.extended_submission_date - summary["today"]).days + 1

    assert summary["submitting_cohort_days_remaining"] == expected_days


@pytest.mark.django_db
def test_cohort_summary_without_organisation_is_audit_wide():
    """Default behaviour (no organisation) is unchanged: audit-wide dates."""
    submitting = AuditPeriod.objects.currently_submitting()
    assert submitting is not None, "No seeded cohort is currently submitting."

    summary = AuditPeriod.objects.cohort_summary()

    assert summary["submitting_cohort_dates"]["extended_submission_date"] is None
    assert summary["submitting_cohort_submission_date"] == submitting.submission_deadline


@pytest.mark.django_db
def test_cohort_summary_grace_card_falls_back_to_most_recently_closed():
    """The first card always has a cohort: when no cohort is in grace (the
    common case - grace lasts only weeks), the card shows the most recently
    closed cohort rather than an empty dict."""
    summary = AuditPeriod.objects.cohort_summary()

    grace_card = summary["grace_cohort"]
    assert grace_card != {}, (
        "grace_cohort card dict was empty - the dashboard's first card would "
        "render with no cohort number or dates."
    )

    if summary["within_grace_period"]:
        # during grace the card shows the grace cohort
        grace_period = AuditPeriod.objects.is_grace_period()
        assert grace_card["cohort"] == grace_period.cohort_number
    else:
        # otherwise the most recently closed cohort
        closed = AuditPeriod.objects.most_recently_closed()
        assert closed is not None
        assert grace_card["cohort"] == closed.cohort_number
        assert grace_card["is_extension_eligible"] is False


# ---------------------------------------------------------------------------
# deadline resolution with close-early extensions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_extension_earlier_than_deadline_wins(GOSH):
    """A close-early extension (date before the audit-wide deadline) is honoured."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    early = COHORT_6_SUBMISSION_DEADLINE - timedelta(days=7)
    AuditPeriodExtension.objects.create(
        audit_period=audit_period,
        organisation=GOSH,
        extended_submission_date=early,
        reason=None,
    )

    assert audit_period.submission_deadline_for_organisation(GOSH) == early


@pytest.mark.django_db
def test_extension_earlier_than_deadline_passes_clean(GOSH):
    """clean() permits close-early dates (but not dates before data collection)."""
    audit_period = AuditPeriod.objects.by_cohort(6)
    extension = AuditPeriodExtension(
        audit_period=audit_period,
        organisation=GOSH,
        extended_submission_date=COHORT_6_SUBMISSION_DEADLINE - timedelta(days=7),
    )
    extension.clean()  # should not raise

    extension.extended_submission_date = (
        audit_period.data_collection_start_date - timedelta(days=1)
    )
    with pytest.raises(ValidationError):
        extension.clean()


@pytest.mark.django_db
def test_card_dict_flags_close_early_extension(GOSH):
    """The card distinguishes close-early rows from true extensions."""
    audit_period = AuditPeriod.objects.by_cohort(6)

    AuditPeriodExtension.objects.create(
        audit_period=audit_period,
        organisation=GOSH,
        extended_submission_date=COHORT_6_SUBMISSION_DEADLINE - timedelta(days=3),
    )
    card = audit_period.as_cohort_card_dict(
        today=COHORT_6_DATA_COLLECTION, organisation=GOSH
    )
    assert card["is_closed_early"] is True

    # a later extension is not closed early
    extension = AuditPeriodExtension.objects.get(
        audit_period=audit_period, organisation=GOSH
    )
    extension.extended_submission_date = COHORT_6_SUBMISSION_DEADLINE + timedelta(days=3)
    extension.save()
    card = audit_period.as_cohort_card_dict(
        today=COHORT_6_DATA_COLLECTION, organisation=GOSH
    )
    assert card["is_closed_early"] is False


# ---------------------------------------------------------------------------
# close_submission_for_organisation / remove_submission_extension
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_close_submission_sets_extension_to_today(GOSH):
    """Closing sets the extension date to today, with no reason required."""
    audit_period = AuditPeriod.objects.currently_submitting()
    assert audit_period is not None, "No seeded cohort is currently submitting."
    admin = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    extension = audit_period.close_submission_for_organisation(GOSH, user=admin)

    assert extension.extended_submission_date == date.today()
    assert extension.reason is None
    assert audit_period.submission_deadline_for_organisation(GOSH) == date.today()


@pytest.mark.django_db
def test_remove_submission_extension_reverts_to_audit_wide(GOSH):
    """Removing the extension reverts the organisation to the audit-wide deadline."""
    audit_period = AuditPeriod.objects.currently_submitting()
    assert audit_period is not None, "No seeded cohort is currently submitting."
    admin = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    _extension(audit_period, GOSH, days=28)
    assert audit_period.extensions.filter(organisation=GOSH).exists()

    audit_period.remove_submission_extension(GOSH, user=admin)

    assert not audit_period.extensions.filter(organisation=GOSH).exists()
    assert (
        audit_period.submission_deadline_for_organisation(GOSH)
        == audit_period.submission_deadline
    )


@pytest.mark.django_db
def test_remove_submission_extension_without_extension_raises(GOSH):
    """Removing an extension the organisation does not hold is an error."""
    audit_period = AuditPeriod.objects.currently_submitting()
    assert audit_period is not None, "No seeded cohort is currently submitting."
    admin = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    with pytest.raises(ValidationError, match="no extension"):
        audit_period.remove_submission_extension(GOSH, user=admin)
