# Python imports
from dateutil.relativedelta import relativedelta
from datetime import date

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import SEX_TYPE, KPI_SCORE
from epilepsy12.models import (
    AntiEpilepsyMedicine,
    Medicine,
    Registration,
    KPI,
)


@pytest.mark.parametrize(
    "over_12, valproate, topiramate, is_a_pregnancy_prevention_programme_in_place, has_a_valproate_annual_risk_acknowledgement_form_been_completed,expected_score",
    [
        # PASS scenarios
        (
            True,
            False,
            True,
            True,
            True,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on topiramate with both prevention measures
        (
            True,
            False,
            True,
            True,
            False,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on topiramate with prevention programme
        (
            True,
            False,
            True,
            False,
            True,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on topiramate with risk form
        (
            False,
            True,
            False,
            True,
            False,
            KPI_SCORE["PASS"],
        ),  # <12yo female on valproate with prevention programme
        (
            False,
            True,
            False,
            False,
            True,
            KPI_SCORE["PASS"],
        ),  # <12yo female on valproate with risk form
        (
            False,
            True,
            False,
            True,
            True,
            KPI_SCORE["PASS"],
        ),  # <12yo female on valproate with both prevention measures
        (
            True,
            True,
            False,
            True,
            False,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on valproate with prevention programme
        (
            True,
            True,
            False,
            False,
            True,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on valproate with risk form
        (
            True,
            True,
            False,
            True,
            True,
            KPI_SCORE["PASS"],
        ),  # >=12yo female on valproate with both prevention measures
        (
            False,
            True,
            False,
            None,
            True,
            KPI_SCORE["PASS"],
        ),  # <12yo female on valproate with unknown prevention programme
        (
            False,
            True,
            False,
            True,
            None,
            KPI_SCORE["PASS"],
        ),  # <12yo female on valproate with unknown risk form
        # FAIL scenarios
        (
            True,
            False,
            True,
            False,
            False,
            KPI_SCORE["FAIL"],
        ),  # >=12yo female on topiramate with no prevention measures
        (
            False,
            True,
            False,
            False,
            False,
            KPI_SCORE["FAIL"],
        ),  # <12yo female on valproate with no prevention measures
        (
            True,
            True,
            False,
            False,
            False,
            KPI_SCORE["FAIL"],
        ),  # >=12yo female on valproate with no prevention measures
        (
            True,
            False,
            True,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # >=12yo female on topiramate with both unknown
        (
            False,
            True,
            False,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # <12yo female on valproate with both unknown
        (
            True,
            True,
            False,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # >=12yo female on valproate with both unknown
        # INELIGIBLE scenarios
        (
            False,
            False,
            False,
            True,
            True,
            KPI_SCORE["INELIGIBLE"],
        ),  # <12yo female not on valproate or topiramate
        (
            False,
            False,
            False,
            False,
            False,
            KPI_SCORE["INELIGIBLE"],
        ),  # <12yo female not on valproate or topiramate
        (
            True,
            False,
            False,
            True,
            True,
            KPI_SCORE["INELIGIBLE"],
        ),  # >=12yo female not on valproate or topiramate
        (
            True,
            False,
            False,
            False,
            False,
            KPI_SCORE["INELIGIBLE"],
        ),  # >=12yo female not on valproate or topiramate
        (
            True,
            False,
            False,
            None,
            None,
            KPI_SCORE["INELIGIBLE"],
        ),  # >=12yo female not on valproate or topiramate
    ],
)
@pytest.mark.django_db
def test_measure_8_sodium_valproate_risk_eligible_cohort_7_and_above(
    e12_case_factory,
    over_12,
    valproate,
    topiramate,
    is_a_pregnancy_prevention_programme_in_place,
    has_a_valproate_annual_risk_acknowledgement_form_been_completed,
    expected_score,
):
    """
    Note this test is only for cohort 7 and above
    *PASS*
    1) (age_at_first_paediatric_assessment >= 12 && sex == 2 && medicine is topiramate) AND ONE OF:
            - is_a_pregnancy_prevention_programme_in_place==True
            - has_a_valproate_annual_risk_acknowledgement_form_been_completed==True
        or
        (sex == 2 && medicine is valproate) AND ONE OF:
            - is_a_pregnancy_prevention_programme_in_place==True
            - has_a_valproate_annual_risk_acknowledgement_form_been_completed==True
    *FAIL*
    1) (age_at_first_paediatric_assessment >= 12 && sex == 2 && medicine is Topiramate) AND NEITHER are True
            - is_a_pregnancy_prevention_programme_in_place
            - has_a_valproate_annual_risk_acknowledgement_form_been_completed
        or
        (age_at_first_paediatric_assessment < 12 && sex == 2 && medicine is valproate) AND NEITHER  are True
            - is_a_pregnancy_prevention_programme_in_place
            - has_a_valproate_annual_risk_acknowledgement_form_been_completed

    """

    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(
        2024, 1, 1
    )  # cohort 7 - note that this test is only for cohort 7 and above
    if over_12:
        DATE_OF_BIRTH = FIRST_PAEDIATRIC_ASSESSMENT_DATE - relativedelta(years=13)
    else:
        DATE_OF_BIRTH = FIRST_PAEDIATRIC_ASSESSMENT_DATE - relativedelta(years=11)
    SEX = SEX_TYPE[2][0]

    # create case
    case = e12_case_factory(
        sex=SEX,
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__management__has_an_aed_been_given=True,
    )

    # get management
    management = case.registration.management

    # clean current AEMs if any are set
    AntiEpilepsyMedicine.objects.filter(management=management).delete()

    # create and save a valproate AEM entry with paramtrized constants
    if topiramate:
        medicine = Medicine.objects.get(conceptId="777808008")  # topiramate
    elif valproate:
        medicine = Medicine.objects.get(conceptId="387481005")  # valproate
    else:
        medicine = Medicine.objects.get(conceptId="776508005")  # Keppra

    AntiEpilepsyMedicine.objects.create(
        management=management,
        is_rescue_medicine=False,
        medicine_entity=medicine,
        antiepilepsy_medicine_risk_discussed=True,
        is_a_pregnancy_prevention_programme_in_place=is_a_pregnancy_prevention_programme_in_place,
        has_a_valproate_annual_risk_acknowledgement_form_been_completed=has_a_valproate_annual_risk_acknowledgement_form_been_completed,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(pk=registration.kpi.pk).sodium_valproate

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"{'>=12yo' if over_12 else '<12yo'} on {'valproate' if valproate else ''}{'topiramate' if topiramate else ''} with valproate pregnancy prevention in place & has: {'annual risk acknowledgement=True' if has_a_valproate_annual_risk_acknowledgement_form_been_completed else ''} {'is_a_pregnancy_prevention_programme_in_place=True' if is_a_pregnancy_prevention_programme_in_place else ''}, but not passing measure"
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"{'>=12yo' if over_12 else '<12yo'} on {'valproate' if valproate else ''}{'topiramate' if topiramate else ''} with valproate pregnancy prevention in place & has: {'annual risk acknowledgement=True' if has_a_valproate_annual_risk_acknowledgement_form_been_completed else ''} {'is_a_pregnancy_prevention_programme_in_place=True' if is_a_pregnancy_prevention_programme_in_place else ''}, but not failing measure"
    elif expected_score == KPI_SCORE["NOT_SCORED"]:
        assertion_message = f"{'>=12yo' if over_12 else '<12yo'} on {'valproate' if valproate else ''}{'topiramate' if topiramate else ''} with valproate pregnancy prevention in place & has: {'annual risk acknowledgement=True' if has_a_valproate_annual_risk_acknowledgement_form_been_completed else ''} {'is_a_pregnancy_prevention_programme_in_place=True' if is_a_pregnancy_prevention_programme_in_place else ''}, but not returning NOT SCORED measure"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    "age, sex, aed_given, not_valproate, topiramate, expected_score",
    [
        (
            relativedelta(years=11, months=11),
            SEX_TYPE[2][0],
            True,
            True,
            False,
            KPI_SCORE["INELIGIBLE"],
        ),  # 11y11mo, F, aed given, topiramate
        (
            relativedelta(years=12),
            SEX_TYPE[1][0],
            True,
            True,
            False,
            KPI_SCORE["INELIGIBLE"],
        ),  # 12yo, M, aed given, topiramate, not valproate
        (
            relativedelta(years=12),
            SEX_TYPE[2][0],
            False,
            True,
            False,
            KPI_SCORE["INELIGIBLE"],
        ),  # 12yo, F, aed NOT given, NO valproate
    ],
)
@pytest.mark.django_db
def test_measure_8_cohort_7_and_above_ineligible(
    e12_case_factory, age, sex, aed_given, not_valproate, topiramate, expected_score
):
    """
    *INELIGIBLE*
    1) age_at_first_paediatric_assessment < 12 and topiramate (without valproate)
    2) registration_instance.case.sex == 1
    3) registration_instance.management.has_an_aed_been_given == False
    4) AEM is not valproate and not topiramate or AEM is None

    Note this test is only for cohort 7 and above
    """
    # Explicitly set paramtrized age and sex
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2024, 1, 1)  # cohort 7
    DATE_OF_BIRTH = FIRST_PAEDIATRIC_ASSESSMENT_DATE - age
    SEX = sex

    # create case
    case = e12_case_factory(
        sex=SEX,
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    )

    # get management
    management = case.registration.management

    # get current AEMs
    aem = AntiEpilepsyMedicine.objects.filter(management=management)

    # clean current aems
    aem.delete()

    if aed_given:
        # AED given, update management
        management.has_an_aed_been_given = True
        management.save()

        # create and save an AEM entry which ISN'T valproate
        if not_valproate:
            AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                medicine_entity=Medicine.objects.get(medicine_name="Lorazepam"),
            )
        # create and save a valproate AEM entry. Only case is <12yoF or 12yoM
        else:
            AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
                antiepilepsy_medicine_risk_discussed=True,
            )

        if topiramate:
            AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                medicine_entity=Medicine.objects.get(medicine_name="Topiramate"),
            )

    else:
        # no AED given, update management
        management.has_an_aed_been_given = False
        management.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(pk=registration.kpi.pk).sodium_valproate

    # set assertion error reason
    if aed_given and not_valproate:
        assertion_message = f"Not on valproate yet not being scored as ineligible"
    else:
        if age == relativedelta(years=11, months=11):
            reason = "age is 11y11m (<12y)"
        elif sex == SEX_TYPE[1][0]:
            reason = "male"
        elif not aed_given:
            reason = "no AED given"
        assertion_message = (
            f"On valproate but {reason} yet not being scored as ineligible"
        )

    assert kpi_score == expected_score, assertion_message
