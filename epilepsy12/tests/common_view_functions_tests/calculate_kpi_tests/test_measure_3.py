"""
Tests for Measure 3 `tertiary_input.

Each test depends on whether child has been AT LEAST ONE OF:
    - received input by neurologist within 1 year of first paediatric assessment
    - referred to epilepsy surgery within 1 year of first paediatric assessment
The eligibiltity criteria for the test include:
    - age at first paediatric assessment is less than 3 years
    - child is on 3 or more anti-epilepsy medicines
    - child has generalised myoclonic epilepsy or focal myoclonic epilepsy and is under 4 years old
    - meet criteria for epilepsy surgery

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

from epilepsy12.common_view_functions.calculate_kpi_functions import (
    calculate_age_at_first_paediatric_assessment_in_years,
)

# sets up paramtrization constant for running tests against seen neurologist/surgery/both/neither

CASE_PARAM_NAMES = "DATE_OF_BIRTH, FIRST_PAEDIATRIC_ASSESSMENT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, PAEDIATRIC_NEUROLOGIST_INPUT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE, expected_kpi_score"
THREEB_CASE_PARAM_NAMES = "DATE_OF_BIRTH, FIRST_PAEDIATRIC_ASSESSMENT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE, expected_kpi_score, error_message"
date_of_birth = date(2021, 1, 1)
first_paediatric_assessment_date_under_3 = date(2023, 1, 1)  # exactly 2yo
first_paediatric_assessment_date_under_4 = date(2024, 12, 1)  # date at age 3y 11mths
first_paediatric_assessment_date_over_4 = date(2025, 12, 1)  # date at age 3y 11mths
input_referral_date_pass_fpa_under_3 = date(
    2024, 1, 1
)  # 1 year after first_paediatric_assessment_date
input_referral_date_fail_under_3 = date(
    2025, 1, 1
)  # 2 year after first_paediatric_assessment_date
input_referral_date_pass_fpa_under_4 = date(
    2025, 1, 1
)  # 1 year after first_paediatric_assessment_date
input_referral_date_fail_under_4 = date(
    2026, 1, 1
)  # 2 year after first_paediatric_assessment_date
# CASE_PARAM_VALUES = [
#     (input_date, True, KPI_SCORE["PASS"]),
#     (input_date, False, KPI_SCORE["PASS"]),
#     (None, True, KPI_SCORE["PASS"]),
#     (None, False, KPI_SCORE["FAIL"]),
# ]
cess_referral_date_pass = date(
    2025, 1, 1  # 1 month after first_paediatric_assessment_date
)
cess_referral_date_fail = date(2026, 1, 1)  # 2 year after
cess_referral_date_empty = None
cess_criteria_met = True
cess_referral_made = True
cess_referral_not_made = False
cess_referral_made_empty = None
cess_criteria_not_met = False
cess_criteria_not_scored = None


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    # CASE_PARAM_VALUES,
    [
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            False,
            input_referral_date_pass_fpa_under_3,
            None,
            KPI_SCORE["PASS"],
        ),  # age < 3, seen neurologist within 1 year
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            True,
            None,
            input_referral_date_pass_fpa_under_3,
            KPI_SCORE["PASS"],
        ),  # age < 3, seen surgery within 1 year
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            False,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),  # age < 3, not seen neurologist/referred surgery within 1 year
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            True,
            None,
            input_referral_date_fail_under_3,
            KPI_SCORE["FAIL"],
        ),  # age < 3, not seen neurologist but referred surgery beyond 1 year
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            False,
            input_referral_date_fail_under_3,
            None,
            KPI_SCORE["FAIL"],
        ),  # age < 3, seen neurologist beyond 1 year, not referred surgery
    ],
)
@pytest.mark.django_db
def test_measure_3_age_3yo(
    e12_case_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    expected_kpi_score,
):
    """
    *PASS*
    1) age at First Paediatric Assessment (FPA) is <= 3 && ONE OF:
        - input by neurologist within 1 year
        - CESS referral within 1 year
    *FAIL*
    1) age at First Paediatric Assessment (FPA) is <= 3 && NOT seen by neurologist OR CESS referral within 1 year
    """

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    if PAEDIATRIC_NEUROLOGIST_INPUT_DATE:
        val = (
            "Age at FPA is 3yo and seen by neurologist within 1 year"
            if PAEDIATRIC_NEUROLOGIST_INPUT_DATE + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else "Age at FPA is 3yo and seen by neurologist beyond 1 year"
        )
    elif CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE:
        val = (
            "Age at FPA is 3yo and referred to CESS within 1 year"
            if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE
            + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else "Age at FPA is 3yo and referred to CESS beyond 1 year"
        )
    assert (
        kpi_score == expected_kpi_score
    ), f"{val} but did not {'fail' if expected_kpi_score == 0 else 'pass'} measure"


# "DATE_OF_BIRTH, FIRST_PAEDIATRIC_ASSESSMENT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, PAEDIATRIC_NEUROLOGIST_INPUT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE, expected_kpi_score"
@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    [
        (
            date_of_birth,
            first_paediatric_assessment_date_under_3,
            False,
            input_referral_date_pass_fpa_under_3,
            None,
            KPI_SCORE["PASS"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_3_3AEMs_seen(
    e12_case_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    expected_kpi_score,
):
    #     """
    #     *PASS*
    #     1) child is on 3 or more AEMS && ONE OF:
    #         - input by BOTH neurologist
    #         - CESS referral
    #     *FAIL*
    #     1) child is on 3 or more AEMS && eithr NOT seen within 1 y by (neurologist OR epilepsy surgery)
    #     *INELIGIBLE*
    #       child ion < 3 AEMS and has no other eligibilities and seen by neurologist / referred surgery within 1 year
    #     """

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
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

    if PAEDIATRIC_NEUROLOGIST_INPUT_DATE:
        val = (
            f"Age at FPA is 3yo and seen by neurologist within 1 year and on {aems_count} AEMS"
            if PAEDIATRIC_NEUROLOGIST_INPUT_DATE + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else "Age at FPA is 3yo and seen by neurologist beyond 1 year"
        )
    elif CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE:
        val = (
            f"Age at FPA is 3yo and referred to CESS within 1 yea and on {aems_count} AEMS"
            if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE
            + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else "Age at FPA is 3yo and referred to CESS beyond 1 year"
        )
    assert (
        kpi_score == expected_kpi_score
    ), f"{val} but did not {'fail' if expected_kpi_score == 0 else 'pass'} measure"

    # Now remove an AEM, increase age to >3y and check if the score changes to ineligible if not on 3 AEMs
    # and not met criteria for surgery.
    AntiEpilepsyMedicine.objects.filter(
        management=registration.management,
        is_rescue_medicine=False,
        antiepilepsy_medicine_start_date__lt=registration.completed_first_year_of_care_date,
    ).first().delete()
    case.registration.first_paediatric_assessment_date = (
        first_paediatric_assessment_date_under_4
    )
    case.registration.save()
    case.refresh_from_db()
    number_of_aems = AntiEpilepsyMedicine.objects.filter(
        management=case.registration.management,
        is_rescue_medicine=False,
        antiepilepsy_medicine_start_date__lt=case.registration.completed_first_year_of_care_date,
    ).count()
    if not CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET:
        calculate_kpis(registration_instance=case.registration)
        kpi_score = KPI.objects.get(pk=case.registration.kpi.pk).tertiary_input
        assert (
            kpi_score == KPI_SCORE["INELIGIBLE"]
        ), f"Age at FPA is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}, not eligible for surgery and on {number_of_aems} drugs but did not return ineligible"


# "DATE_OF_BIRTH, FIRST_PAEDIATRIC_ASSESSMENT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET, PAEDIATRIC_NEUROLOGIST_INPUT_DATE, CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE, expected_kpi_score"
@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    [
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            False,
            input_referral_date_pass_fpa_under_4,
            None,
            KPI_SCORE["PASS"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            True,
            None,
            input_referral_date_pass_fpa_under_4,
            KPI_SCORE["PASS"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            False,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            True,
            None,
            input_referral_date_fail_under_4,
            KPI_SCORE["FAIL"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            False,
            input_referral_date_fail_under_4,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_over_4,
            False,
            None,
            None,
            KPI_SCORE["INELIGIBLE"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_3_lt_4yo_generalised_myoclonic_seen(
    e12_case_factory,
    e12_episode_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is under 4 and has myoclonic epilepsy && no other eligibilities ONE OF:
        - input by neurologist within 1 year OR
        - CESS referral within 1 year
    *FAIL*
    1) child is under 4 and has myoclonic epilepsy && NOT seen by (neurologist OR epilepsy surgery)
    *INELIGIBLE*
    1) child is > 4y and has myoclonic epilepsy && no other eligibilities and seen by neurologist / referred surgery within 1 year
    """

    # SET UP CONSTANTS
    MYOCLONIC = GENERALISED_SEIZURE_TYPE[5][0]

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a myoclonic episode
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        epileptic_generalised_onset=MYOCLONIC,
        epilepsy_or_nonepilepsy_status="E",
    )

    # count myoclonic episodes attached to confirm
    episodes = Episode.objects.filter(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epilepsy_or_nonepilepsy_status="E",
        epileptic_generalised_onset=MYOCLONIC,
    )

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    if PAEDIATRIC_NEUROLOGIST_INPUT_DATE:
        val = (
            f"Has myoclonic episode (n = {episodes.count()}) and seen by neurologist within 1 year"
            if PAEDIATRIC_NEUROLOGIST_INPUT_DATE + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else "Has myoclonic episode (n = {episodes.count()}) and seen by neurologist beyond 1 year"
        )
    elif CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE:
        val = (
            f"Has myoclonic episode (n = {episodes.count()}) and referred to CESS within 1 year"
            if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE
            + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else f"Has myoclonic episode (n = {episodes.count()}) and referred to CESS beyond 1 year"
        )
    else:
        val = f"Has myoclonic episode (n = {episodes.count()}) at age {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}"

    if expected_kpi_score == KPI_SCORE["INELIGIBLE"]:
        val += " but did not return ineligible"
    elif expected_kpi_score == KPI_SCORE["FAIL"]:
        val += " but did not fail measure"
    elif expected_kpi_score == KPI_SCORE["PASS"]:
        val += " but did not pass measure"

    assert kpi_score == expected_kpi_score, f"{val}"


@pytest.mark.parametrize(
    CASE_PARAM_NAMES,
    [
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            False,
            input_referral_date_pass_fpa_under_4,
            None,
            KPI_SCORE["PASS"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            True,
            None,
            input_referral_date_pass_fpa_under_4,
            KPI_SCORE["PASS"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            False,
            input_referral_date_fail_under_4,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            True,
            None,
            input_referral_date_fail_under_4,
            KPI_SCORE["FAIL"],
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_over_4,
            False,
            None,
            None,
            KPI_SCORE["INELIGIBLE"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_3_lt_4yo_focal_myoclonic_seen(
    e12_case_factory,
    e12_episode_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    expected_kpi_score,
):
    """
    *PASS*
    1) child is under 4 and has myoclonic epilepsy && ONE OF:
        - input by neurologist within 1 year OR
        - CESS referral within 1 year
    *FAIL*
    1) child is under 4 and has myoclonic epilepsy && NOT seen by (neurologist OR referred to epilepsy surgery) within 1 year
    *INELIGIBLE*
    1) child is > 4y and has myoclonic epilepsy && no other eligibilities and seen by neurologist / referred surgery within 1 year
    """

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__paediatric_neurologist_input_date=PAEDIATRIC_NEUROLOGIST_INPUT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a myoclonic episode
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        epilepsy_or_nonepilepsy_status="E",
        focal_onset_myoclonic=True,
    )

    # count myoclonic episodes attached to confirm
    episodes = Episode.objects.filter(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epilepsy_or_nonepilepsy_status="E",
        focal_onset_myoclonic=True,
    )

    calculate_kpis(registration_instance=registration)

    if expected_kpi_score == KPI_SCORE["INELIGIBLE"]:
        # delete the episode to make the case ineligible
        episodes = Episode.objects.filter(
            multiaxial_diagnosis=registration.multiaxialdiagnosis,
            epilepsy_or_nonepilepsy_status="E",
            focal_onset_myoclonic=True,
        ).delete()

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    if PAEDIATRIC_NEUROLOGIST_INPUT_DATE:
        val = (
            f"Is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}y and has myoclonic episode (n = {episodes.count()}) and seen by neurologist within 1 year"
            if PAEDIATRIC_NEUROLOGIST_INPUT_DATE + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else f"Is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}y and has myoclonic episode (n = {episodes.count()}) and seen by neurologist beyond 1 year"
        )
    elif CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE:
        val = (
            f"Is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}y and has myoclonic episode (n = {episodes.count()}) and referred to CESS within 1 year"
            if CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE
            + relativedelta(years=1)
            >= FIRST_PAEDIATRIC_ASSESSMENT_DATE
            else f"Is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}y and has myoclonic episode (n = {episodes.count()}) and referred to CESS beyond 1 year"
        )
    else:
        val = f"Is {calculate_age_at_first_paediatric_assessment_in_years(case.registration)}y and myoclonic episodes removed)"

    if expected_kpi_score == KPI_SCORE["INELIGIBLE"]:
        val += " but did not return ineligible"
    elif expected_kpi_score == KPI_SCORE["FAIL"]:
        val += " but did not fail measure"
    elif expected_kpi_score == KPI_SCORE["PASS"]:
        val += " but did not pass measure"

    assert kpi_score == expected_kpi_score, f"{val}"


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

    # default N(AEMs) = 1, override not required

    # <4y without myoclonic epilepsy
    OTHER = GENERALISED_SEIZURE_TYPE[-1][0]

    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date_under_4,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=False,  # not eligible epilepsy surgery criteria
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # Assign a NON-MYOCLONIC episode (OTHER)
    e12_episode_factory.create(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        epileptic_seizure_onset_type_generalised=True,
        epileptic_generalised_onset=OTHER,
        epilepsy_or_nonepilepsy_status="E",
    )

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).tertiary_input

    assert (
        kpi_score == KPI_SCORE["INELIGIBLE"]
    ), f"Child does not meet any criteria but is not scoring as ineligible"


# CESS 3b


@pytest.mark.parametrize(
    THREEB_CASE_PARAM_NAMES,
    [
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_met,
            cess_referral_made,
            cess_referral_date_pass,
            KPI_SCORE["PASS"],
            "cess_criteria_met, cess_referral_date_pass - should pass",
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_met,
            cess_referral_made,
            cess_referral_date_fail,
            KPI_SCORE["FAIL"],
            "cess_criteria_met, cess_referral_date_fail - should fail",
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_met,
            cess_referral_made_empty,
            cess_referral_date_fail,
            KPI_SCORE["FAIL"],
            "cess_criteria_met, cess_referral_made_empty, cess_referral_date_fail - should fail",
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_not_met,
            cess_referral_made_empty,
            cess_referral_date_empty,
            KPI_SCORE["INELIGIBLE"],
            "cess_criteria_not_met, cess_referral_date_empty - should be ineligible",
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_met,
            cess_referral_made_empty,
            cess_referral_date_empty,
            KPI_SCORE["NOT_SCORED"],
            "cess_criteria_met, cess_referral_date_empty - should not be scored",
        ),
        (
            date_of_birth,
            first_paediatric_assessment_date_under_4,
            cess_criteria_not_scored,
            cess_referral_made_empty,
            cess_referral_date_empty,
            KPI_SCORE["NOT_SCORED"],
            "cess_criteria_not_scored, cess_referral_date_empty - should not be scored",
        ),
    ],
)
@pytest.mark.django_db
def test_measure_3b_meets_CESS_seen(
    e12_case_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
    CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    expected_kpi_score,
    error_message,
):
    """
    Epilepsy surgery referral - % of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral
    *PASS*
    1) child is eligible for epilepsy surgery (assessment.childrens_epilepsy_surgical_service_referral_criteria_met) && ONE OF:
        (- childrens_epilepsy_surgical_service_referral_made)
        - childrens_epilepsy_surgical_service_referral_date within 1 year of first paediatric assessment
    *FAIL*
    1) child is eligible for epilepsy surgery (assessment.childrens_epilepsy_surgical_service_referral_criteria_met) && Referral date beyond 1 year or not referred
    *INELIGIBLE*
    1) child is not eligible for epilepsy surgery (assessment.childrens_epilepsy_surgical_service_referral_criteria_met = False
    """

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_MADE,
        registration__assessment__childrens_epilepsy_surgical_service_referral_criteria_met=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_surgery_referral

    assert kpi_score == expected_kpi_score, f"{error_message}"
