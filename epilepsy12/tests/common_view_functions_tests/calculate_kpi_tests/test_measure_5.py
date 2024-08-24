"""
Measure 5 `mri`

Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic or Epilepsy with generalized tonic–clonic seizures alone at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request

=

COUNT(kids)
AND
    NOT (JME or JAE or CAE or CECTS/Rolandic or Epilepsy with generalized tonic–clonic seizures alone) 

AND
    had MRI within 6 weeks of request

- [ x] Measure 5 passed (registration.kpi.mri == 1) if MRI done in 6 weeks and are NOT JME or JAE or CAE or CECTS/Rolandic or Epilepsy with generalized tonic–clonic seizures alone (lines 270-324)
- [ x] Measure 5 failed (registration.kpi.mri == 0) if MRI not done in 6 weeks and are NOT JME or JAE or CAE or CECTS/Rolandic or Epilepsy with generalized tonic–clonic seizures alone (lines 270-324)
- [ x] Measure 5 ineligible (registration.kpi.mri == 0) if JME or JAE or CAE or CECTS/Rolandic or Epilepsy with generalized tonic–clonic seizures alone
"""

# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports
from django.contrib.gis.db.models import Q

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
    Syndrome,
    SyndromeList,
    MultiaxialDiagnosis,
)
from epilepsy12.constants import (
    KPI_SCORE,
    SYNDROMES,
)


@pytest.mark.parametrize(
    "DATE_OF_BIRTH,FIRST_PAEDIATRIC_ASSESSMENT_DATE,TIMELY_MRI,EXPECTED_SCORE",
    [
        (
            # <2yo, MRI done within 6 weeks of refer
            date(2022, 1, 1),
            date(2023, 12, 31),
            True,
            KPI_SCORE["PASS"],
        ),
        (  # 2yo, MRI NOT done within 6 weeks of refer
            date(2022, 1, 1),
            date(2023, 12, 31),
            False,
            KPI_SCORE["FAIL"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_5_mri_under2yo(
    e12_case_factory,
    DATE_OF_BIRTH,
    FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    TIMELY_MRI,
    EXPECTED_SCORE,
):
    """
    *PASS*
    1) MRI done in 6 weeks post-referral
    *FAIL*
    1) MRI NOT done in 6 weeks post-referral
    """
    MRI_REQUESTED_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE + relativedelta(days=1)

    MRI_REPORTED_DATE = MRI_REQUESTED_DATE + relativedelta(weeks=6)
    if not TIMELY_MRI:
        MRI_REPORTED_DATE = MRI_REQUESTED_DATE + relativedelta(weeks=6, days=1)

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__investigations__mri_brain_requested_date=MRI_REQUESTED_DATE,
        registration__investigations__mri_brain_reported_date=MRI_REPORTED_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).mri

    if EXPECTED_SCORE == KPI_SCORE["PASS"]:
        assert (
            kpi_score == EXPECTED_SCORE
        ), f"MRI booked <= 6 weeks but not passing measure"
    elif EXPECTED_SCORE == KPI_SCORE["FAIL"]:
        assert (
            kpi_score == EXPECTED_SCORE
        ), f"MRI booked > 6 weeks but not failing measure"


@pytest.mark.parametrize(
    "TIMELY_MRI,EXPECTED_SCORE",
    [
        (
            #  MRI done within 6 weeks of refer
            True,
            KPI_SCORE["PASS"],
        ),
        (  #  MRI NOT done within 6 weeks of refer
            False,
            KPI_SCORE["FAIL"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_5_mri_syndromes_pass_fail(
    e12_case_factory, TIMELY_MRI, EXPECTED_SCORE
):
    """
    *PASS*
    1) MRI done in 6 weeks post-referral and are NOT (JME or JAE or CAE or CECTS/Rolandic)
    *FAIL*
    1) MRI NOT done in 6 weeks post-referral and are NOT (JME or JAE or CAE or CECTS/Rolandic)
    """
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2023, 1, 1)

    MRI_REQUESTED_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE + relativedelta(days=1)

    MRI_REPORTED_DATE = MRI_REQUESTED_DATE + relativedelta(weeks=6)
    if not TIMELY_MRI:
        MRI_REPORTED_DATE += relativedelta(days=1)

    case = e12_case_factory(
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__investigations__mri_brain_requested_date=MRI_REQUESTED_DATE,
        registration__investigations__mri_brain_reported_date=MRI_REPORTED_DATE,
    )

    # set syndrome present to False
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        registration=case.registration
    )
    multiaxial_diagnosis.syndrome_present = False
    multiaxial_diagnosis.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # get attached syndromes
    relevant_syndromes = Syndrome.objects.filter(
        Q(multiaxial_diagnosis=registration.multiaxialdiagnosis)
        &
        # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
        Q(
            syndrome__syndrome_name__in=[
                "Self-limited epilepsy with centrotemporal spikes",
                "Juvenile myoclonic epilepsy",
                "Juvenile absence epilepsy",
                "Childhood absence epilepsy",
                "Generalised tonic clonic seizures only",
            ]
        )
    )
    # remove syndromes to ensure just testing pass/fail
    if relevant_syndromes.exists():
        relevant_syndromes.delete()

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).mri

    if EXPECTED_SCORE == KPI_SCORE["PASS"]:
        assert (
            kpi_score == EXPECTED_SCORE
        ), f"None of JME or JAE or CAE or CECTS/Rolandi present, MRI booked <= 6 weeks but not passing measure"

    elif EXPECTED_SCORE == KPI_SCORE["FAIL"]:
        assert (
            kpi_score == EXPECTED_SCORE
        ), f"None of JME or JAE or CAE or CECTS/Rolandi present, MRI booked > 6 weeks but not failing measure"


@pytest.mark.parametrize(
    "SYNDROME_TYPE_PRESENT",
    [
        (SYNDROMES[18][1]),  # Juvenile myoclonic epilepsy
        (SYNDROMES[17][1]),  # Juvenile absence epilepsy
        (SYNDROMES[16][1]),  # Childhood absence epilepsy
        (SYNDROMES[3][1]),  # Self-limited epilepsy with centrotemporal spikes
        (SYNDROMES[19][1]),  # Generalised tonic clonic seizures only
    ],
)
@pytest.mark.django_db
def test_measure_5_mri_syndromes_ineligible(
    e12_case_factory, e12_syndrome_factory, SYNDROME_TYPE_PRESENT
):
    """
    *INELIGIBLE*
    1)      ONE OF:
                JME or JAE or CAE or CECTS/Rolandic or Generalised tonic clonic seizures only
    """

    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2023, 1, 1)
    DATE_OF_BIRTH = FIRST_PAEDIATRIC_ASSESSMENT_DATE - relativedelta(years=2)

    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
    )

    # set syndrome present to True
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        registration=case.registration
    )
    multiaxial_diagnosis.syndrome_present = True
    multiaxial_diagnosis.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    # ensure starting with no default syndromes
    Syndrome.objects.filter(
        multiaxial_diagnosis=registration.multiaxialdiagnosis
    ).delete()

    # save the ineligible syndrome type
    new_syndrome = e12_syndrome_factory(
        multiaxial_diagnosis=registration.multiaxialdiagnosis,
        syndrome=SyndromeList.objects.get(syndrome_name=SYNDROME_TYPE_PRESENT),
    )
    new_syndrome.save()

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).mri

    # ensure we get syndromes from db
    SYNDROME_TYPE_PRESENT = Syndrome.objects.get(
        multiaxial_diagnosis=registration.multiaxialdiagnosis
    )
    assert (
        kpi_score == KPI_SCORE["INELIGIBLE"]
    ), f"{SYNDROME_TYPE_PRESENT} present, should be ineligible"
