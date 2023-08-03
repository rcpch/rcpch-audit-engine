# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE

def score_kpi_10(registration_instance, age_at_first_paediatric_assessment) -> int:
    """10. school_individual_healthcare_plan
    
    Percentage of children and young people with epilepsy aged 5 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.
    
    Calculation Method
    
    Numerator = Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP
    
    Denominator =Number of children and young people aged 5 years and above diagnosed with epilepsy at first year
    """

    management = registration_instance.management

    # ineligible
    if age_at_first_paediatric_assessment < 5:
        return KPI_SCORE["INELIGIBLE"]

    # unscored
    if management.individualised_care_plan_includes_ehcp is None:
        return KPI_SCORE["NOT_SCORED"]

    # score kpi
    if management.individualised_care_plan_includes_ehcp is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
