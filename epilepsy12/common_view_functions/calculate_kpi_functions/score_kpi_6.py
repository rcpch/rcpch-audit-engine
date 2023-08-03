# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE


def score_kpi_6(registration_instance, age_at_first_paediatric_assessment) -> int:
    """6. assessment_of_mental_health_issues

    Calculation Method

    Numerator = Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health

    Denominator = = Number of children and young people over 5 years diagnosed with epilepsy
    """

    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis

    # ineligible
    if age_at_first_paediatric_assessment < 5:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if multiaxial_diagnosis.mental_health_screen is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if multiaxial_diagnosis.mental_health_screen:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
