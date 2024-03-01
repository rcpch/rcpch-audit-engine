"""
Tests for Measure 3 `tertiary_input.

Each test depends on whether child has been AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery

- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if age at first paediatric assessment is < 3 AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is on 3 or more AEMS (see lines 115-120 for query) and AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is under 4 and has myoclonic epilepsy (lines 128-133) and AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if age at first paediatric assessment is < 3 and not AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery ( where age_at_first_paediatric_assessment = relativedelta(registration_instance.first_paediatric_assessment_date,registration_instance.case.date_of_birth).years)
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is on 3 or more AEMS (see lines 115-120 for query) and not AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is under 4 and has myoclonic epilepsy (lines 128-133) and not AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and not AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery
- [ ] Measure 3 ineligible (registration.kpi.tertiary_input == 2) if age at first paediatric assessment is > 3 and not not on 3 or more drugs and not eligible for epilepsy surgery and not >4y with myoclonic epilepsy
Measure 3b
- [ ] Measure 3b passed (registration.kp.epilepsy_surgery_referral ==1 ) if met criteria for surgery and evidence of referral or being seen (line 224)

    PASS IF ANY OF:
        1. (age <= 3yo at first assessment) AND (AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery)
        2. ((age < 4yo) AND (myoclonic epilepsy)) AND (AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery)
        3. (on >= 3 AEMS) AND (AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery)
        4. (eligible for epilepsy surgery) AND (AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery)
    OR MORE SIMPLY:
        If *criteria met* AND *referred/AT LEAST ONE OF:
    - received input by neurologist 
    - referred to epilepsy surgery*
"""

# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
    AntiEpilepsyMedicine,
    Medicine,
    Episode,
)
from epilepsy12.constants import (
    KPI_SCORE,
    GENERALISED_SEIZURE_TYPE,
)

# sets up paramtrization constant for running tests against seen neurologist/surgery/both/neither

CASE_PARAM_NAMES = "PAEDIATRIC_NEUROLOGIST_INPUT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE, expected_kpi_score"
input_date = date(2023, 1, 1)
CASE_PARAM_VALUES = [
    (input_date, True, KPI_SCORE["PASS"]),
    (input_date, False, KPI_SCORE["PASS"]),
    (None, True, KPI_SCORE["PASS"]),
    (None, False, KPI_SCORE["FAIL"]),
]


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    CASE_PARAM_VALUES,
)
@pytest.mark.django_db
def test_measure_3_age_3yo(
    e12_case_factory,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    expected_kpi_score,
):
    """
    *PASS*
    1) age at First Paediatric Assessment (FPA) is <= 3 && ONE OF:
        - input by BOTH neurologist
        - CESS referral
    *FAIL*
    1) age at First Paediatric Assessment (FPA) is <= 3 && NOT seen by neurologist OR CESS referral
    """

    # a child who is exactly 3 at first_paediatric_assessment_date (=FPA)
    DATE_OF_BIRTH = date(2021, 1, 1)
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = DATE_OF_BIRTH + relativedelta(years=3)

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert kpi_score == expected_kpi_score, (
        f"Age at FPA is 3yo and {'seen by neurologist' if PAEDIATRIC_NEUROLOGIST_INPUT_DATE else ''}  {'referred to CESS' if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE else ''} but did not pass measure"
        if expected_kpi_score == KPI_SCORE["PASS"]
        else f"Age at FPA is 3yo but not seen by either neurologist / surgery and did not fail measure"
    )


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    CASE_PARAM_VALUES,
)
@pytest.mark.django_db
def test_measure_3_3AEMs_seen(
    e12_case_factory,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is on 3 or more AEMS && ONE OF:
        - input by BOTH neurologist
        - CESS referral
    *FAIL*
    1) child is on 3 or more AEMS && NOT seen by (neurologist OR epilepsy surgery)
    """

    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(
        2023, 1, 1
    )  # explicit setting to ensure aems started before registration close date

    case = e12_case_factory(
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # create total of 3 AEMs related to this registration instance (already has 1 by default so only add 2)
    aems_to_add = Medicine.objects.filter(
        medicine_name__in=["Zonisamide", "Vigabatrin"]
    )
    for aem_to_add in aems_to_add:
        new_aem = AntiEpilepsyMedicine.objects.create(
            management=registration.management,
            medicine_entity=aem_to_add,
            is_rescue_medicine=False,
            antiepilepsy_medicine_start_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE
            + relativedelta(days=5),
        )
        new_aem.save()
    aems_count = AntiEpilepsyMedicine.objects.filter(
        management=registration.management,
        is_rescue_medicine=False,
        antiepilepsy_medicine_start_date__lt=registration.completed_first_year_of_care_date,
    ).count()

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert kpi_score == expected_kpi_score, (
        f"On >= 3 AEMS (n={aems_count}) and seen by neurologist / epilepsy surgery/both but did not pass measure"
        if expected_kpi_score == KPI_SCORE["PASS"]
        else f"On >= 3 AEMS (n={aems_count}) and not seen by neurologist / surgery and did not fail measure"
    )


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    CASE_PARAM_VALUES,
)
@pytest.mark.django_db
def test_measure_3_lt_4yo_generalised_myoclonic_seen(
    e12_case_factory,
    e12_episode_factory,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is under 4 and has myoclonic epilepsy && ONE OF:
        - input by BOTH neurologist
        - CESS referral
    *FAIL*
    1) child is under 4 and has myoclonic epilepsy && NOT seen by (neurologist OR epilepsy surgery)
    """

    # SET UP CONSTANTS
    DATE_OF_BIRTH = date(2021, 1, 1)
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = DATE_OF_BIRTH + relativedelta(
        years=3, months=11
    )  # a child who is 3y11m at first_paediatric_assessment_date (=FPA)
    MYOCLONIC = GENERALISED_SEIZURE_TYPE[5][0]

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a myoclonic episode
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        epileptic_generalised_onset=MYOCLONIC,
    )

    # count myoclonic episodes attached to confirm
    episodes = Episode.objects.filter(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epilepsy_or_nonepilepsy_status="E",
        epileptic_generalised_onset=MYOCLONIC,
    )

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert kpi_score == expected_kpi_score, (
        f"Has myoclonic episode (n = {episodes.count()}) and seen by {'neurologist' if PAEDIATRIC_NEUROLOGIST_INPUT_DATE else ''} / {'epilepsy surgery' if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE else ''} but did not pass measure"
        if expected_kpi_score == KPI_SCORE["PASS"]
        else f"Has myoclonic episode (n = {episodes.count()}) and not seen by neurologist both surgery and did not fail measure"
    )


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    CASE_PARAM_VALUES,
)
@pytest.mark.django_db
def test_measure_3_lt_4yo_focal_myoclonic_seen(
    e12_case_factory,
    e12_episode_factory,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is under 4 and has myoclonic epilepsy && ONE OF:
        - input by BOTH neurologist
        - CESS referral
    *FAIL*
    1) child is under 4 and has myoclonic epilepsy && NOT seen by (neurologist OR epilepsy surgery)
    """

    # SET UP CONSTANTS
    DATE_OF_BIRTH = date(2021, 1, 1)
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = DATE_OF_BIRTH + relativedelta(
        years=3, months=11
    )  # a child who is 3y11m at first_paediatric_assessment_date (=FPA)

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a myoclonic episode
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        focal_onset_myoclonic=True,
    )

    # count myoclonic episodes attached to confirm
    episodes = Episode.objects.filter(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epilepsy_or_nonepilepsy_status="E",
        focal_onset_myoclonic=True,
    )

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert kpi_score == expected_kpi_score, (
        f"Has myoclonic episode (n = {episodes.count()}) and seen by {'neurologist' if PAEDIATRIC_NEUROLOGIST_INPUT_DATE else ''} / {'epilepsy surgery' if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE else ''} but did not pass measure"
        if expected_kpi_score == KPI_SCORE["PASS"]
        else f"Has myoclonic episode (n = {episodes.count()}) and not seen by neurologist both surgery and did not fail measure"
    )


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    CASE_PARAM_VALUES,
)
@pytest.mark.django_db
def test_measure_3b_meets_CESS_seen(
    e12_case_factory,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is eligible for epilepsy surgery (assessment.childrens_epilepsy_surgical_service_referral_criteria_met) && ONE OF:
        - input by BOTH neurologist
        - CESS referral
    *FAIL*
    1) child is eligible for epilepsy surgery (assessment.childrens_epilepsy_surgical_service_referral_criteria_met) && NOT seen by (neurologist OR epilepsy surgery)
    """

    case = e12_case_factory(
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=True,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_surgery_referral

    assert kpi_score == expected_kpi_score, (
        f"Met CESS criteria and {'seen by neurologist' if PAEDIATRIC_NEUROLOGIST_INPUT_DATE else ''}  {'referred to CESS' if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE else ''} but did not pass measure"
        if expected_kpi_score == KPI_SCORE["PASS"]
        else f"Met CESS criteria and not seen by neurologist / surgery and did not fail measure"
    )


@pytest.mark.django_db
def test_measure_3_ineligible(
    e12_case_factory,
    e12_episode_factory,
):
    """
    *INELIGIBLE*
    1) age at first paediatric assessment is > 3y
        and
        not on 3 or more drugs
        and
        not >4y with myoclonic epilepsy
        and
        not eligible for epilepsy surgery
    """

    # a child who is exactly 3y1mo at first_paediatric_assessment_date (=FPA)
    DATE_OF_BIRTH = date(2021, 1, 1)
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = DATE_OF_BIRTH + relativedelta(
        years=4,
    )

    # default N(AEMs) = 1, override not required

    # <4y without myoclonic epilepsy
    OTHER = GENERALISED_SEIZURE_TYPE[-1][0]

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=False,  # not eligible epilepsy surgery criteria
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a NON-MYOCLONIC episode (OTHER)
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        epileptic_generalised_onset=OTHER,
    )

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert (
        kpi_score == KPI_SCORE["INELIGIBLE"]
    ), f"Child does not meet any criteria but is not scoring as ineligible"
