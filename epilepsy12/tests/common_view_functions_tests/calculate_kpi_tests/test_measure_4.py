"""
Measure 4 `ecg`

% of children and young people with convulsive seizures and epilepsy, with an ECG at first year

- [x] Measure 4 passed (registration.kpi.ecg == 1) if ECG performed and seizure convulsive (registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive and registration_instance.investigations.twelve_lead_ecg_status)
- [x] Measure 4 failed (registration.kpi.ecg == 0) if ECG not performed and seizure convulsive (not registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive and registration_instance.investigations.twelve_lead_ecg_status)
- [x] Measure 4 ineligible (registration.kpi.ecg == 2) if seizure not convulsive (not registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive)
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
)
from epilepsy12.constants import (
    KPI_SCORE,
)


@pytest.mark.parametrize(
    "CONVULSIVE_SEIZURE,ECG_STATUS,EXPECTED_SCORE",
    [
        (True, True, KPI_SCORE["PASS"]),
        (True, False, KPI_SCORE["FAIL"]),
        (False, False, KPI_SCORE["INELIGIBLE"]),
    ],
)
@pytest.mark.django_db
def test_measure_4_ecg_for_convulsive_seizure(
    e12_case_factory,
    CONVULSIVE_SEIZURE,
    ECG_STATUS,
    EXPECTED_SCORE,
):
    """
    *PASS*
    1) seizure convulsive + ECG performed
    *FAIL*
    1) seizure convulsive + no ECG
    *INELIGIBLE*
    1) seizure not convulsive
    """

    case = e12_case_factory(
        registration__epilepsy_context__were_any_of_the_epileptic_seizures_convulsive=CONVULSIVE_SEIZURE,
        registration__investigations__twelve_lead_ecg_status=ECG_STATUS,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).ecg

    # INELIGIBLE CASE
    if EXPECTED_SCORE == KPI_SCORE["INELIGIBLE"]:
        assert (
            kpi_score == EXPECTED_SCORE
        ), f"Seizure not convulsive, (no ECG) but not being scored as ineligible"

    # PASS / FAIL CASES
    assert (
        kpi_score == EXPECTED_SCORE
    ), f"Seizure convulsive, {'' if KPI_SCORE['PASS'] else 'no'} ECG performed, but not {'pass' if KPI_SCORE['PASS'] else 'fail'}ing measure"


@pytest.mark.parametrize(
    "CONVULSIVE_SEIZURE,ECG_STATUS,EXPECTED_SCORE",
    [
        (None, True, KPI_SCORE["NOT_SCORED"]),
        (True, None, KPI_SCORE["NOT_SCORED"]),
    ],
)
@pytest.mark.django_db
def test_measure_4_not_scored(
    e12_case_factory, CONVULSIVE_SEIZURE, ECG_STATUS, EXPECTED_SCORE
):
    """
    *NOT SCORED*
    1) seizure convulsive is None
    2) twelve_lead_ecg_status is None
    """

    case = e12_case_factory(
        registration__epilepsy_context__were_any_of_the_epileptic_seizures_convulsive=CONVULSIVE_SEIZURE,
        registration__investigations__twelve_lead_ecg_status=ECG_STATUS,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).ecg

    # define assertion message
    reason = "Convulsive seizure" if not registration.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive else "ECG field"
    
    # NOT SCORED
    assert kpi_score == EXPECTED_SCORE, f"{reason} field is None but not being scored as 'NOT_SCORED'"
