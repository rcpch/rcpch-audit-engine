# python imports

# django imports
from django.contrib.gis.db.models import Q

# E12 imports
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import AntiEpilepsyMedicine, Episode

def score_kpi_3(registration_instance, age_at_first_paediatric_assessment) -> int:
    """3. tertiary_input
    % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care

    Calculation Method

    Numerator = Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]

    Denominator = Number of children [less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year )OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] OR (Number of children less than 4 years old at first assessment with epilepsy AND  [myoclonic seizures])
    """

    assessment = registration_instance.assessment

    # EVALUATE ELIGIBILITY CRITERIA

    # first gather relevant data
    aems_count = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        is_rescue_medicine=False,
        antiepilepsy_medicine_start_date__lt=registration_instance.registration_close_date,
    ).count()
    has_myoclonic_epilepsy_episode = Episode.objects.filter(
        Q(multiaxial_diagnosis=registration_instance.multiaxialdiagnosis)
        & Q(epilepsy_or_nonepilepsy_status="E")
        & Q(epileptic_generalised_onset="MyC")
    ).exists()

    # List of True/False assessing if meets any of criteria
    eligibility_criteria = [
        (age_at_first_paediatric_assessment <= 3),
        (age_at_first_paediatric_assessment < 4 and has_myoclonic_epilepsy_episode),
        (aems_count >= 3),
        (
            assessment.childrens_epilepsy_surgical_service_referral_criteria_met
        ),  # NOTE: CESS_referral_criteria_met is only one that could be None (rest must be True/False), however, only checking whether it is True or not True here so doesn't matter
    ]

    # None of eligibility criteria are True -> set ineligible with guard clause
    if not any(eligibility_criteria):
        return KPI_SCORE["INELIGIBLE"]

    # Eligible for measure - EVALUATE IF AT LEAST REFERRED FROM NEUROLOGIST OR CESS. NOTE: technically the Assessment model allows a referral_date & input_date filled WITHOUT referral_made, but this is a rare edge case just for API-use. The UI does not allow you to enter either date, if referral_made is False. If the API has an endpoint for this measure, need to ensure referral_made==True, if dates are both valid.

    # first evaluate relevant fields complete
    tertiary_input_complete = (
        assessment.paediatric_neurologist_referral_made is not None
    ) or (assessment.childrens_epilepsy_surgical_service_referral_made is not None)

    if not tertiary_input_complete:
        return KPI_SCORE["NOT_SCORED"]

    pass_criteria = [
        (assessment.paediatric_neurologist_referral_made is True),
        (assessment.childrens_epilepsy_surgical_service_referral_made is True),
    ]

    # if referral made to either neurologist or CESS, they pass
    if any(pass_criteria):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]

def score_kpi_3b(registration_instance) -> int:
    """3b. epilepsy_surgery_referral

    % of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral
    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy AND met [CESS criteria] at first year AND had [evidence of referral or involvement of CESS]

    Denominator = Number of children and young people diagnosed with epilepsy AND met CESS criteria at first year
    """

    assessment = registration_instance.assessment

    # not scored
    if assessment.childrens_epilepsy_surgical_service_referral_criteria_met is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if assessment.childrens_epilepsy_surgical_service_referral_criteria_met is False:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if (
        assessment.childrens_epilepsy_surgical_service_referral_made is None
        and assessment.paediatric_neurologist_referral_made is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score KPI
    if (
        assessment.childrens_epilepsy_surgical_service_referral_made
        or assessment.paediatric_neurologist_referral_made
    ):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]
