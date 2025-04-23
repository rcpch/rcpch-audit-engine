# python imports

# django imports
from django.apps import apps
from django.db.models import Q

# E12 imports
from epilepsy12.constants import KPI_SCORE


def score_kpi_8(registration_instance, age_at_first_paediatric_assessment) -> int:
    AntiEpilepsyMedicine = apps.get_model("epilepsy12", "AntiEpilepsyMedicine")
    Medicine = apps.get_model("epilepsy12", "Medicine")

    """
    8. sodium_valproate
    
    Title: Medication and Reproductive Risks

    Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

    Calculation Method
    
    Numerator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate AND 
    (
    annual risk acknowledgement forms completed 
    OR 
    pregnancy prevention programme in place
    )
    
    Denominator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate
    """
    # ineligible - < 12yo or male
    if age_at_first_paediatric_assessment < 12 or registration_instance.case.sex != 2:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if registration_instance.management.has_an_aed_been_given is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if not AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
    ).exists():
        return KPI_SCORE["INELIGIBLE"]

    # get valproate assigned
    valproate = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.filter(
            medicine_name="Sodium valproate"
        ).first(),
    ).first()

    # not scored
    if (
        valproate.is_a_pregnancy_prevention_programme_in_place is None
        or valproate.has_a_valproate_annual_risk_acknowledgement_form_been_completed
        is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    if (
        valproate.is_a_pregnancy_prevention_programme_in_place
        or valproate.has_a_valproate_annual_risk_acknowledgement_form_been_completed
    ):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_8_topiramate(
    registration_instance, age_at_first_paediatric_assessment
) -> int:
    AntiEpilepsyMedicine = apps.get_model("epilepsy12", "AntiEpilepsyMedicine")
    Medicine = apps.get_model("epilepsy12", "Medicine")

    """
    Title: KPI 8: Medication and Reproduction Risks - Topiramate: Note this only applies to cohort 7

    Description: Percentage of females on valproate treatment and females aged 12 years and above on topiramate with a risk acknowledgement form completed or Pregnancy Prevention Programme in place

    Numerator:
    (Number of all females on valproate OR females aged 12 years and above on topiramate)
    AND
    (Evidence of a risk acknowledgement form completed OR a Pregnancy Prevention Programme in place)

    Denominator:
    Number of all females on valproate OR females aged 12 years and above on topiramate
    """
    # set up parameters
    male = registration_instance.case.sex == 1
    female = registration_instance.case.sex == 2
    age_12_or_above = age_at_first_paediatric_assessment >= 12

    valproate_prescribed = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.get(conceptId="387481005"),  # valproate
    ).exists()
    topiramate_prescribed = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.get(conceptId="777808008"),  # topiramate
    ).exists()
    a_pregnancy_prevention_programme_is_in_place = False
    a_valproate_annual_risk_acknowledgement_form_been_completed = False

    if valproate_prescribed:
        valproate = AntiEpilepsyMedicine.objects.filter(
            management=registration_instance.management,
            medicine_entity=Medicine.objects.get(conceptId="387481005"),  # valproate
        ).first()
        a_pregnancy_prevention_programme_is_in_place = (
            valproate.is_a_pregnancy_prevention_programme_in_place
        )
        a_valproate_annual_risk_acknowledgement_form_been_completed = (
            valproate.has_a_valproate_annual_risk_acknowledgement_form_been_completed
        )
    if topiramate_prescribed:
        topiramate = AntiEpilepsyMedicine.objects.filter(
            management=registration_instance.management,
            medicine_entity=Medicine.objects.get(conceptId="777808008"),  # topiramate
        ).first()
        a_pregnancy_prevention_programme_is_in_place = (
            topiramate.is_a_pregnancy_prevention_programme_in_place
        )
        if female:
            a_valproate_annual_risk_acknowledgement_form_been_completed = (
                topiramate.has_a_valproate_annual_risk_acknowledgement_form_been_completed
            )

    # ineligible - exclude boys
    if male:
        return KPI_SCORE["INELIGIBLE"]

    #  ineligible - exclude those  not on valproate and not ( >12 and on topiramate)
    if not valproate_prescribed and not (age_12_or_above and topiramate_prescribed):
        return KPI_SCORE["INELIGIBLE"]

    # ineligible - no AED has been given
    if not registration_instance.management.has_an_aed_been_given:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if registration_instance.management.has_an_aed_been_given is None:
        return KPI_SCORE["NOT_SCORED"]

    # by this point an AED has been given, either valproate or topiramate and female is True
    # not scored if a girl any age on valproate or a girl >= 12 on topiramate and either of risk acknowledgement form or pregnancy prevention programme is None
    if (
        a_pregnancy_prevention_programme_is_in_place is None
        and a_valproate_annual_risk_acknowledgement_form_been_completed is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    if (age_12_or_above and topiramate_prescribed) or valproate_prescribed:
        if a_pregnancy_prevention_programme_is_in_place or (
            a_valproate_annual_risk_acknowledgement_form_been_completed
        ):
            return KPI_SCORE["PASS"]

    # Edge case if on both valproate and topiramate  - only need one of the two conditions to be true
    if valproate_prescribed and topiramate_prescribed:
        if any(
            [
                topiramate.has_a_valproate_annual_risk_acknowledgement_form_been_completed,
                topiramate.is_a_pregnancy_prevention_programme_in_place,
                valproate.has_a_valproate_annual_risk_acknowledgement_form_been_completed,
                valproate.is_a_pregnancy_prevention_programme_in_place,
            ]
        ):
            return KPI_SCORE["PASS"]

    # any other combination of conditions will fail the measure
    return KPI_SCORE["FAIL"]
