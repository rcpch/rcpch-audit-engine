# python imports

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE


def score_kpi_2(registration_instance) -> int:
    """2. epilepsy_specialist_nurse

    % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

    Calculation Method

    Numerator= Number of children and young people [diagnosed with epilepsy] AND who had [input from or referral to an Epilepsy Specialist Nurse] by first year

    Denominator = Number of children and young people [diagnosed with epilepsy] at first year
    """

    assessment = registration_instance.assessment

    # no nurse referral, fail
    if assessment.epilepsy_specialist_nurse_referral_made is False:
        return KPI_SCORE["FAIL"]

    # if not all filled, incomplete form
    if (
        assessment.epilepsy_specialist_nurse_referral_made is None
        or assessment.epilepsy_specialist_nurse_referral_date is None
        or assessment.epilepsy_specialist_nurse_input_date is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score check
    has_seen_nurse_before_close_date = (
        assessment.epilepsy_specialist_nurse_input_date
        <= registration_instance.registration_close_date
        or assessment.epilepsy_specialist_nurse_referral_date
        <= registration_instance.registration_close_date
    )

    if has_seen_nurse_before_close_date:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
