# python imports

# django imports
from django.contrib.gis.db.models import Q
from django.apps import apps

# E12 imports
# from epilepsy12.models import Syndrome
from epilepsy12.constants import KPI_SCORE


def score_kpi_5(registration_instance, age_at_first_paediatric_assessment) -> int:
    """5. MRI

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic OR number of children aged under 2 years at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request
    
    Denominator = Number of children and young people diagnosed with epilepsy at first year AND ((who are NOT JME or JAE or CAE or BECTS) OR (number of children aged under  2 years  at first assessment with a diagnosis of epilepsy at first year))
    """
    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis
    investigations = registration_instance.investigations

    Syndrome = apps.get_model("epilepsy12", "Syndrome")

    # not scored
    if (age_at_first_paediatric_assessment >= 2) and (
        multiaxial_diagnosis.syndrome_present is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # define eligibility criteria 1
    ineligible_syndrome_present = Syndrome.objects.filter(
        Q(multiaxial_diagnosis=multiaxial_diagnosis)
        &
        # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
        Q(
            syndrome__syndrome_name__in=[
                "Self-limited epilepsy with centrotemporal spikes",
                "Juvenile myoclonic epilepsy",
                "Juvenile absence epilepsy",
                "Childhood absence epilepsy",
            ]
        )
    ).exists()

    # check eligibility criteria 1 & 2
    # 1 = none of the specified syndromes present
    # 2 = age in years < 2
    if (not ineligible_syndrome_present) or (age_at_first_paediatric_assessment < 2):
        # not scored
        mri_dates_are_none = [
            (investigations.mri_brain_requested_date is None),
            (investigations.mri_brain_reported_date is None),
        ]
        if any(mri_dates_are_none):
            return KPI_SCORE["NOT_SCORED"]

        # eligible for this measure - score kpi
        passing_criteria_met = (
            abs(
                (
                    investigations.mri_brain_requested_date
                    - investigations.mri_brain_reported_date
                ).days
            )
            <= 42
        )

        if passing_criteria_met:
            return KPI_SCORE["PASS"]
        else:
            return KPI_SCORE["FAIL"]

    # ineligible
    else:
        return KPI_SCORE["INELIGIBLE"]
