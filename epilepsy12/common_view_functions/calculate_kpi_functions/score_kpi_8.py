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
    age_below_12 = age_at_first_paediatric_assessment < 12
    valproate = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.get(conceptId="387481005"),  # valproate
    ).exists()
    topiramate = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        medicine_entity=Medicine.objects.get(conceptId="387481005"),  # topiramate
    ).exists()

    # ineligible - Not on valproate and not ( >12 and on topiramate) or male
    if male or not (valproate and (age_below_12 and topiramate)):
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if registration_instance.management.has_an_aed_been_given is None:
        return KPI_SCORE["NOT_SCORED"]

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
    ) and (female and (age_12_or_above and topiramate) or valproate):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
