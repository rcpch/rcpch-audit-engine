# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE

def score_kpi_4(registration_instance) -> int:
    """4. ECG

    % of children and young people with convulsive seizures and epilepsy, with an ECG at first year

    Calculation Method
    
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year AND who have [12 lead ECG obtained]
    
    Denominator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year
    """
    epilepsy_context = registration_instance.epilepsycontext
    investigations = registration_instance.investigations

    # ineligible
    if epilepsy_context.were_any_of_the_epileptic_seizures_convulsive is False:
        return KPI_SCORE["INELIGIBLE"]
    
    # not scored / ineligible guard clauses
    if (epilepsy_context.were_any_of_the_epileptic_seizures_convulsive is None) or (
        investigations.twelve_lead_ecg_status is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # Convulsive seizure - score ECG status

    if investigations.twelve_lead_ecg_status is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
