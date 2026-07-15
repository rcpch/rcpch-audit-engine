"""
Tests for AuditProgress.audit_progress_fields_incomplete — the "missing fields"
popup path.

This file is the popup-side counterpart to
epilepsy12/tests/view_tests/form_calculations/test_total_fields_expected.py,
which covers the scoring path (total_fields_expected). The two paths must agree:
a field that is not counted as "expected" by the scoring path must also be
absent from the popup's missing-fields list, and vice versa.

These tests pin the conditional-exclusion logic in
AuditProgress.exclude_fields_from_audit_progress for the Investigations model,
with particular focus on:

  * cohort gating — genome sequencing fields (genome_sequencing_requested +
    R14/R27/R59 status and date fields) must not appear for cohort < 8;
  * the genome gate — for cohort >= 8, the R14/R27/R59 family is only expected
    when genome_sequencing_requested is True; the gate question itself is always
    expected for cohort 8+;
  * per-test status — when genome is requested, R14/R27/R59 date fields are
    conditional on the test_status (None/N hides both dates, R hides
    achieved_date only, A hides nothing);
  * EEG/MRI date fields hidden when their gating question is false/None;
  * the None-audit-period regression — registrations without an audit_period
    (no first paediatric assessment date, or legacy/test data) must not raise
    and must be treated as "not cohort 8".

Assertions check both presence of expected labels and absence of excluded
labels, so that a regression in either direction is caught.
"""

from datetime import date

import pytest

from epilepsy12.models import Registration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Labels are taken from the Investigations help_text "label" values, since
# AuditProgress._field_label prefers help_text["label"] over verbose_name.
GENOME_GATE_LABEL = "Has epilepsy related Whole Genome Sequencing been requested?"
R14_STATUS_LABEL = "Was an R14 test requested?"
R27_STATUS_LABEL = "Was an R27 test requested?"
R59_STATUS_LABEL = "Was an R59 test requested?"
R14_REQUESTED_DATE_LABEL = "Date of decision to request R14 test"
R14_ACHIEVED_DATE_LABEL = "Date R14 test result achieved"
R27_REQUESTED_DATE_LABEL = "Date of decision to request R27 test"
R27_ACHIEVED_DATE_LABEL = "Date R27 test result achieved"
R59_REQUESTED_DATE_LABEL = "Date of decision to request R59 test"
R59_ACHIEVED_DATE_LABEL = "Date R59 test result achieved"

EEG_REQUEST_DATE_LABEL = "Date EEG requested"
EEG_PERFORMED_DATE_LABEL = "Date EEG performed"
MRI_REQUESTED_DATE_LABEL = "MRI brain requested date"
MRI_REPORTED_DATE_LABEL = "Date MRI brain reported"


def _missing_investigations_labels(case) -> set:
    """Return the set of missing-field labels for the case's investigations."""
    audit_progress = case.registration.audit_progress
    return set(
        audit_progress.audit_progress_fields_incomplete(model_name="investigations")
    )


def _make_cohort8_case(e12_case_factory, GOSH, **investigations_kwargs):
    """Build a cohort-8 case with the given investigations field overrides."""
    factory_kwargs = {
        "first_name": f"temp_child_{GOSH.name}",
        "organisations__organisation": GOSH,
    }
    for k, v in investigations_kwargs.items():
        factory_kwargs[f"registration__investigations__{k}"] = v
    case = e12_case_factory(**factory_kwargs)
    # cohort 8: FPA date in 2025 (matches the convention in test_total_fields_expected.py)
    case.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    case.registration.save()
    assert case.registration.audit_period.cohort_number == 8
    return case


# ---------------------------------------------------------------------------
# Cohort < 8: genome fields not expected at all
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cohort_lt8_excludes_all_genome_fields(e12_case_factory, GOSH):
    """
    Cohort < 8: even if genome_sequencing_requested is True and test statuses
    are set, none of the genome fields should appear in the missing list.
    The default factory FPA date (2023-01-01) yields cohort 6.
    """
    case = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__genome_sequencing_requested=True,
        registration__investigations__r14_test_status="A",
        registration__investigations__r27_test_status="R",
        registration__investigations__r59_test_status="N",
    )
    assert case.registration.audit_period.cohort_number < 8

    labels = _missing_investigations_labels(case)

    assert GENOME_GATE_LABEL not in labels
    assert R14_STATUS_LABEL not in labels
    assert R27_STATUS_LABEL not in labels
    assert R59_STATUS_LABEL not in labels
    assert R14_REQUESTED_DATE_LABEL not in labels
    assert R14_ACHIEVED_DATE_LABEL not in labels
    assert R27_REQUESTED_DATE_LABEL not in labels
    assert R27_ACHIEVED_DATE_LABEL not in labels
    assert R59_REQUESTED_DATE_LABEL not in labels
    assert R59_ACHIEVED_DATE_LABEL not in labels


# ---------------------------------------------------------------------------
# Cohort 8, genome gate unanswered / false
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cohort8_genome_none_excludes_tests_only(e12_case_factory, GOSH):
    """
    Cohort 8, genome_sequencing_requested unanswered (None): the gate question
    is still expected (so it appears as missing), but the R14/R27/R59 status
    and date fields are not expected (so they are absent from the missing list).
    """
    case = _make_cohort8_case(e12_case_factory, GOSH)  # genome left as None
    assert case.registration.investigations.genome_sequencing_requested is None

    labels = _missing_investigations_labels(case)

    # The gate question is expected and unanswered -> present in missing list.
    assert GENOME_GATE_LABEL in labels
    # The R14/R27/R59 family is not expected -> absent.
    assert R14_STATUS_LABEL not in labels
    assert R27_STATUS_LABEL not in labels
    assert R59_STATUS_LABEL not in labels
    assert R14_REQUESTED_DATE_LABEL not in labels
    assert R14_ACHIEVED_DATE_LABEL not in labels
    assert R27_REQUESTED_DATE_LABEL not in labels
    assert R27_ACHIEVED_DATE_LABEL not in labels
    assert R59_REQUESTED_DATE_LABEL not in labels
    assert R59_ACHIEVED_DATE_LABEL not in labels


@pytest.mark.django_db
def test_cohort8_genome_false_excludes_tests_only(e12_case_factory, GOSH):
    """
    Cohort 8, genome_sequencing_requested False: the gate is answered (so it is
    NOT missing), and the R14/R27/R59 family is not expected.
    """
    case = _make_cohort8_case(
        e12_case_factory, GOSH, genome_sequencing_requested=False
    )
    labels = _missing_investigations_labels(case)

    # Gate answered False -> not missing.
    assert GENOME_GATE_LABEL not in labels
    # R14/R27/R59 family not expected -> absent.
    assert R14_STATUS_LABEL not in labels
    assert R27_STATUS_LABEL not in labels
    assert R59_STATUS_LABEL not in labels
    assert R14_REQUESTED_DATE_LABEL not in labels
    assert R14_ACHIEVED_DATE_LABEL not in labels
    assert R27_REQUESTED_DATE_LABEL not in labels
    assert R27_ACHIEVED_DATE_LABEL not in labels
    assert R59_REQUESTED_DATE_LABEL not in labels
    assert R59_ACHIEVED_DATE_LABEL not in labels


# ---------------------------------------------------------------------------
# Cohort 8, genome True: per-test status conditions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cohort8_genome_true_all_statuses_none(e12_case_factory, GOSH):
    """
    Cohort 8, genome True, all test statuses unanswered (None): the three
    status questions are expected (present as missing), but their date fields
    are not expected (absent).
    """
    case = _make_cohort8_case(
        e12_case_factory, GOSH, genome_sequencing_requested=True
    )
    labels = _missing_investigations_labels(case)

    # Gate answered True -> not missing.
    assert GENOME_GATE_LABEL not in labels
    # Status questions expected and unanswered -> present.
    assert R14_STATUS_LABEL in labels
    assert R27_STATUS_LABEL in labels
    assert R59_STATUS_LABEL in labels
    # Date fields not expected (status None) -> absent.
    assert R14_REQUESTED_DATE_LABEL not in labels
    assert R14_ACHIEVED_DATE_LABEL not in labels
    assert R27_REQUESTED_DATE_LABEL not in labels
    assert R27_ACHIEVED_DATE_LABEL not in labels
    assert R59_REQUESTED_DATE_LABEL not in labels
    assert R59_ACHIEVED_DATE_LABEL not in labels


@pytest.mark.django_db
def test_cohort8_genome_true_per_test_status_conditions(e12_case_factory, GOSH):
    """
    Cohort 8, genome True, mixed per-test statuses:
      R14 = "A" (Achieved)    -> both dates expected (present as missing)
      R27 = "R" (Requested)   -> requested_date expected, achieved_date NOT
      R59 = "N" (Not Requested) -> neither date expected
    """
    case = _make_cohort8_case(
        e12_case_factory,
        GOSH,
        genome_sequencing_requested=True,
        r14_test_status="A",
        r27_test_status="R",
        r59_test_status="N",
    )
    labels = _missing_investigations_labels(case)

    # Statuses are all answered -> not missing.
    assert R14_STATUS_LABEL not in labels
    assert R27_STATUS_LABEL not in labels
    assert R59_STATUS_LABEL not in labels

    # R14 = "A": both dates expected and unanswered -> present.
    assert R14_REQUESTED_DATE_LABEL in labels
    assert R14_ACHIEVED_DATE_LABEL in labels
    # R27 = "R": requested_date expected, achieved_date NOT expected.
    assert R27_REQUESTED_DATE_LABEL in labels
    assert R27_ACHIEVED_DATE_LABEL not in labels
    # R59 = "N": neither date expected.
    assert R59_REQUESTED_DATE_LABEL not in labels
    assert R59_ACHIEVED_DATE_LABEL not in labels


# ---------------------------------------------------------------------------
# EEG / MRI date gating
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_eeg_indicated_false_excludes_eeg_dates(e12_case_factory, GOSH):
    """
    eeg_indicated False/None: eeg_request_date and eeg_performed_date must not
    appear in the missing list.
    """
    case = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__eeg_indicated=False,
    )
    labels = _missing_investigations_labels(case)

    assert EEG_REQUEST_DATE_LABEL not in labels
    assert EEG_PERFORMED_DATE_LABEL not in labels


@pytest.mark.django_db
def test_mri_indicated_false_excludes_mri_dates(e12_case_factory, GOSH):
    """
    mri_indicated False/None: mri_brain_requested_date and
    mri_brain_reported_date must not appear in the missing list.
    """
    case = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__mri_indicated=False,
    )
    labels = _missing_investigations_labels(case)

    assert MRI_REQUESTED_DATE_LABEL not in labels
    assert MRI_REPORTED_DATE_LABEL not in labels


# ---------------------------------------------------------------------------
# None audit_period regression
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_audit_period_none_does_not_crash_and_excludes_genome(
    e12_case_factory, GOSH
):
    """
    A registration without an audit_period (no FPA date, or legacy/test data)
    must not raise AttributeError. cohort is treated as None -> "not cohort 8",
    so all genome fields are excluded.
    """
    case = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__genome_sequencing_requested=True,
        registration__investigations__r14_test_status="A",
    )
    # Detach the audit_period, mirroring the pattern in test_imd.py.
    Registration.objects.filter(pk=case.registration.pk).update(audit_period=None)
    case.registration.refresh_from_db()
    assert case.registration.audit_period is None

    # Must not raise.
    labels = _missing_investigations_labels(case)

    # Genome family excluded (treated as not cohort 8).
    assert GENOME_GATE_LABEL not in labels
    assert R14_STATUS_LABEL not in labels
    assert R14_REQUESTED_DATE_LABEL not in labels
    assert R14_ACHIEVED_DATE_LABEL not in labels
