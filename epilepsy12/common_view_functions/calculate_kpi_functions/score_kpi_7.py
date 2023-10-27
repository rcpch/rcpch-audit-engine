# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE

def score_kpi_7(registration_instance) -> int:
    """7. mental_health_support

    Percentage of children with epilepsy and a mental health problem who have evidence of mental health support

    Calculation Method
    
    Numerator =  Number of children and young people diagnosed with epilepsy AND had a mental health issue identified AND had evidence of mental health support received
    
    Denominator= Number of children and young people diagnosed with epilepsy AND had a mental health issue identified
    """

    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis
    management = registration_instance.management

    # not scored
    if multiaxial_diagnosis.mental_health_issue_identified is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if multiaxial_diagnosis.mental_health_issue_identified is False:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if management.has_support_for_mental_health_support is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.has_support_for_mental_health_support:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
