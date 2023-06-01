"""
Measure 8 `sodium_valproate` - Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

Number of females >= 12yo diagnosed with epilepsy at first year 
    AND on valproate 
    AND annual risk acknowledgement forms completed 
    AND pregnancy prevention programme in place

- [x] Measure 8 passed (registration.kpi.sodium_valproate == 1) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and is_a_pregnancy_prevention_programme_needed==True and has_a_valproate_annual_risk_acknowledgement_form_been_completed==True
- [x] Measure 8 failed (registration.kpi.sodium_valproate == 0) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and is_a_pregnancy_prevention_programme_needed is False or None
- [x] Measure 8 failed (registration.kpi.sodium_valproate == 0) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and has_a_valproate_annual_risk_acknowledgement_form_been_completed is False or None

- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if age_at_first_paediatric_assessment < 12
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if registration_instance.case.sex == 1
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if registration_instance.management.has_an_aed_been_given == False
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if AEM is not valproate or AEM is None

    # calculate age_at_first_paediatric_assessment
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.registration_date,
        registration_instance.case.date_of_birth,
    ).years

        if (
            age_at_first_paediatric_assessment >= 12
            and registration_instance.case.sex == 2
        ) and (
            registration_instance.management.has_an_aed_been_given
            and AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                medicine_entity=MedicineEntity.objects.filter(
                    medicine_name__icontains="valproate"
                ).first(),
            ).exists()
        ):
            # eligible for this measure
            sodium_valproate = 0
            if (
                age_at_first_paediatric_assessment >= 12
                and registration_instance.case.sex == 2
            ) and (
                registration_instance.management.has_an_aed_been_given
                and AntiEpilepsyMedicine.objects.filter(
                    management=registration_instance.management,
                    medicine_entity=MedicineEntity.objects.filter(
                        medicine_name__icontains="valproate"
                    ).first(),
                    is_a_pregnancy_prevention_programme_needed=True,
                    has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
                ).exists()
            ):
                # criteria met
                sodium_valproate = 1
        else:
            # not eligible for this measure
            sodium_valproate = 2
"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE, SEX_TYPE
from epilepsy12.models import KPI, AntiEpilepsyMedicine, Registration, MedicineEntity


@pytest.mark.parametrize(
    "is_a_pregnancy_prevention_programme_needed, has_a_valproate_annual_risk_acknowledgement_form_been_completed,expected_score",
    [
        (True, True, KPI_SCORE["PASS"]),
        (False, None, KPI_SCORE["FAIL"]),
        (None, False, KPI_SCORE["FAIL"]),
        (None, None, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_8_sodium_valproate_risk_eligible(
    e12_case_factory,
    is_a_pregnancy_prevention_programme_needed,
    has_a_valproate_annual_risk_acknowledgement_form_been_completed,
    expected_score,
):
    """
    *PASS*
    1) (age_at_first_paediatric_assessment >= 12 && sex == 2 && medicine is valproate)
            && is_a_pregnancy_prevention_programme_needed==True
            && has_a_valproate_annual_risk_acknowledgement_form_been_completed==True
    *FAIL*
    1) (age_at_first_paediatric_assessment >= 12 && sex == 2 && medicine is valproate)
            && is_a_pregnancy_prevention_programme_needed is False OR None
    2) (age_at_first_paediatric_assessment >= 12 && sex == 2 && medicine is valproate)
            && has_a_valproate_annual_risk_acknowledgement_form_been_completed is False OR None

    """

    # Explicitly set age to exactly 12yo and sex female (=2)
    REGISTRATION_DATE = date(2023, 1, 1)
    DATE_OF_BIRTH = REGISTRATION_DATE - relativedelta(years=12)
    SEX = SEX_TYPE[2][0]

    # create case
    case = e12_case_factory(
        sex=SEX,
        date_of_birth=DATE_OF_BIRTH,
        registration__registration_date=REGISTRATION_DATE,
    )

    # get management
    management = case.registration.management

    # clean current AEMs
    aem = AntiEpilepsyMedicine.objects.filter(management=management)

    aem.delete()

    # create and save a valproate AEM entry with paramtrized constants
    new_valproate = AntiEpilepsyMedicine.objects.create(
        management=management,
        is_rescue_medicine=False,
        medicine_entity=MedicineEntity.objects.get(medicine_name="Sodium valproate"),
        antiepilepsy_medicine_risk_discussed=True,
        is_a_pregnancy_prevention_programme_needed=is_a_pregnancy_prevention_programme_needed,
        has_a_valproate_annual_risk_acknowledgement_form_been_completed=has_a_valproate_annual_risk_acknowledgement_form_been_completed,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(pk=registration.kpi.pk).sodium_valproate

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f">=12yo on valproate with valproate pregnancy prevention in place & completed annual risk acknowledgement, but not passing measure"
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f">=12yo on valproate with \n{is_a_pregnancy_prevention_programme_needed=}\n{has_a_valproate_annual_risk_acknowledgement_form_been_completed=},\nbut not failing measure"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    "age, sex, aed_given, not_valproate, expected_score",
    [
        (
            relativedelta(years=11, months=11),
            SEX_TYPE[2][0],
            True,
            False,
            KPI_SCORE["NOT_APPLICABLE"],
        ),  # 11y11mo, F, aed given, valproate
        (
            relativedelta(years=12),
            SEX_TYPE[1][0],
            True,
            False,
            KPI_SCORE["NOT_APPLICABLE"],
        ),  # 12yo, M, aed given, valproate
        (
            relativedelta(years=12),
            SEX_TYPE[2][0],
            False,
            True,
            KPI_SCORE["NOT_APPLICABLE"],
        ),  # 12yo, F, aed NOT given, NO valproate
        (
            relativedelta(years=12),
            SEX_TYPE[2][0],
            True,
            True,
            KPI_SCORE["NOT_APPLICABLE"],
        ),  # 12yo, F, aed given, NOT valproate
    ],
)
@pytest.mark.django_db
def test_measure_8_sodium_valproate_risk_ineligible(
    e12_case_factory, age, sex, aed_given, not_valproate, expected_score
):
    """
    *INELIGIBLE*
    1) age_at_first_paediatric_assessment < 12
    2) registration_instance.case.sex == 1
    3) registration_instance.management.has_an_aed_been_given == False
    4) AEM is not valproate or AEM is None

    """

    # Explicitly set paramtrized age and sex
    REGISTRATION_DATE = date(2023, 1, 1)
    DATE_OF_BIRTH = REGISTRATION_DATE - age
    SEX = sex

    # create case
    case = e12_case_factory(
        sex=SEX,
        date_of_birth=DATE_OF_BIRTH,
        registration__registration_date=REGISTRATION_DATE,
    )

    # get management
    management = case.registration.management

    # get current AEMs
    aem = AntiEpilepsyMedicine.objects.filter(management=management)

    # clean current aems
    aem.delete()

    if aed_given:
        # create and save an AEM entry which ISN'T valproate
        if not_valproate:
            new_aem = AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                medicine_entity=MedicineEntity.objects.get(medicine_name="Lorazepam"),
            )

        # create and save a valproate AEM entry. Only case is <12yoF or 12yoM
        else:
            new_valproate = AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                medicine_entity=MedicineEntity.objects.get(
                    medicine_name="Sodium valproate"
                ),
                antiepilepsy_medicine_risk_discussed=True,
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
