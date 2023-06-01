"""
PASS:
- ALL TRUE
FAIL:
- Any false

[x] - 9B `comprehensive_care_planning_content` - Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning.

Number of children and young people diagnosed with epilepsy at first year 
    AND evidence of written prolonged seizures plan if prescribed rescue medication 
    AND evidence of discussion regarding water safety 
    AND first aid 
    AND participation 
    and risk 
    AND service contact details 
    AND SUDEP


[x] - 9Bi. `parental_prolonged_seizures_care_plan` - Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan

Number of children and young people diagnosed with epilepsy at first year 
    AND has_rescue_medication_been_prescribed
    AND individualised_care_plan_parental_prolonged_seizure_care


[x] - 9Bii. `water_safety` - Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety

Number of children and young people diagnosed with epilepsy at first year 
    AND individualised_care_plan_addresses_water_safety


[x] - 9Biii. `first_aid` - Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid

Number of children and young people diagnosed with epilepsy at first year 
    AND individualised_care_plan_include_first_aid


[x] - 9Biv. `general_participation_and_risk` - Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk

Number of children and young people diagnosed with epilepsy at first year 
    AND individualised_care_plan_includes_general_participation_risk


[x] - 9Bv. `service_contact_details` - Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details

Number of children and young people diagnosed with epilepsy at first year 
    AND individualised_care_plan_includes_service_contact_details


[ ] - 9Bvi. `sudep` - Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP AND evidence of a written prolonged seizures plan at first year

Number of children and young people diagnosed with epilepsy at first year 
    AND individualised_care_plan_parental_prolonged_seizure_care
    AND individualised_care_plan_addresses_sudep


"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "has_rescue_medication_been_prescribed,individualised_care_plan_parental_prolonged_seizure_care,individualised_care_plan_include_first_aid,individualised_care_plan_addresses_water_safety,individualised_care_plan_includes_service_contact_details,individualised_care_plan_includes_general_participation_risk,individualised_care_plan_addresses_sudep, expected_score",
    [
        (True, True, True, True, True, True, True, KPI_SCORE["PASS"]),
        (True, False, True, True, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, False, True, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, False, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, False, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, True, False, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, True, True, False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9B_comprehensive_care_planning_content(
    e12_case_factory,
    has_rescue_medication_been_prescribed,
    individualised_care_plan_parental_prolonged_seizure_care,
    individualised_care_plan_include_first_aid,
    individualised_care_plan_addresses_water_safety,
    individualised_care_plan_includes_service_contact_details,
    individualised_care_plan_includes_general_participation_risk,
    individualised_care_plan_addresses_sudep,
    expected_score,
):
    """
    *PASS*
    1) ALL True
    *FAIL*
    1) ANY False
    """

    # create case
    case = e12_case_factory(
        registration__management__has_rescue_medication_been_prescribed=has_rescue_medication_been_prescribed,
        registration__management__individualised_care_plan_parental_prolonged_seizure_care=individualised_care_plan_parental_prolonged_seizure_care,
        registration__management__individualised_care_plan_include_first_aid=individualised_care_plan_include_first_aid,
        registration__management__individualised_care_plan_addresses_water_safety=individualised_care_plan_addresses_water_safety,
        registration__management__individualised_care_plan_includes_service_contact_details=individualised_care_plan_includes_service_contact_details,
        registration__management__individualised_care_plan_includes_general_participation_risk=individualised_care_plan_includes_general_participation_risk,
        registration__management__individualised_care_plan_addresses_sudep=individualised_care_plan_addresses_sudep,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).comprehensive_care_planning_content

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year is True in place but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assessed_measures = [
            "has_rescue_medication_been_prescribed",
            "individualised_care_plan_parental_prolonged_seizure_care",
            "individualised_care_plan_include_first_aid",
            "individualised_care_plan_addresses_water_safety",
            "individualised_care_plan_includes_service_contact_details",
            "individualised_care_plan_includes_general_participation_risk",
            "individualised_care_plan_addresses_sudep",
        ]
        for key, val in vars(registration.management).items():
            if (key in assessed_measures) and not val:
                assertion_message = f"{key} is False but not failing"
                break

    assert kpi_score == expected_score, assertion_message




@pytest.mark.parametrize(
    f"has_rescue_medication_been_prescribed, individualised_care_plan_parental_prolonged_seizure_care, expected_score",
    [
        (True, True, KPI_SCORE["PASS"]),
        (True, False, KPI_SCORE["FAIL"]),
        (False, False, KPI_SCORE["NOT_APPLICABLE"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Bi_parental_prolonged_seizures_care_plan(
    e12_case_factory,
    has_rescue_medication_been_prescribed,
    individualised_care_plan_parental_prolonged_seizure_care,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_parental_prolonged_seizure_care =True 
    *FAIL*
    1) individualised_care_plan_parental_prolonged_seizure_care = False
    *INELIGIBLE*
    1) has_rescue_medication_been_prescribed = False
    """

    # create case
    case = e12_case_factory(
        registration__management__has_rescue_medication_been_prescribed=has_rescue_medication_been_prescribed,
        registration__management__individualised_care_plan_parental_prolonged_seizure_care=individualised_care_plan_parental_prolonged_seizure_care,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).parental_prolonged_seizures_care_plan

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_parental_prolonged_seizure_care is True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_parental_prolonged_seizure_care is False but not failing"
    else:
        assertion_message = f"not on rescue medicine, but not being scored as ineligible"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    f"individualised_care_plan_addresses_water_safety, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Bii_water_safety(
    e12_case_factory,
    individualised_care_plan_addresses_water_safety,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_addresses_water_safety =True 
    *FAIL*
    1) individualised_care_plan_addresses_water_safety = False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_addresses_water_safety=individualised_care_plan_addresses_water_safety,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).water_safety

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_addresses_water_safety is True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_addresses_water_safety is False but not failing"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    f"individualised_care_plan_include_first_aid, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Biii_first_aid(
    e12_case_factory,
    individualised_care_plan_include_first_aid,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_include_first_aid =True 
    *FAIL*
    1) individualised_care_plan_include_first_aid = False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_include_first_aid=individualised_care_plan_include_first_aid,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).first_aid

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_include_first_aid is True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_include_first_aid is False but not failing"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    f"individualised_care_plan_includes_general_participation_risk, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Biv_general_participation_and_risk(
    e12_case_factory,
    individualised_care_plan_includes_general_participation_risk,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_includes_general_participation_risk =True 
    *FAIL*
    1) individualised_care_plan_includes_general_participation_risk = False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_includes_general_participation_risk=individualised_care_plan_includes_general_participation_risk,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).general_participation_and_risk

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_includes_general_participation_risk is True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_includes_general_participation_risk is False but not failing"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    f"individualised_care_plan_includes_service_contact_details, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Bv_service_contact_details(
    e12_case_factory,
    individualised_care_plan_includes_service_contact_details,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_includes_service_contact_details =True 
    *FAIL*
    1) individualised_care_plan_includes_service_contact_details = False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_includes_service_contact_details=individualised_care_plan_includes_service_contact_details,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).service_contact_details

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_includes_service_contact_details is True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_includes_service_contact_details is False but not failing"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.parametrize(
    f"individualised_care_plan_parental_prolonged_seizure_care, individualised_care_plan_addresses_sudep, expected_score",
    [
        (True, True, KPI_SCORE["PASS"]),
        (True, False, KPI_SCORE["FAIL"]),
        (False, True, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Bvi_sudep(
    e12_case_factory,
    individualised_care_plan_parental_prolonged_seizure_care,
    individualised_care_plan_addresses_sudep,
    expected_score,
):
    """
    *PASS*
    1) BOTH True 
    *FAIL*
    1) Either False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_parental_prolonged_seizure_care=individualised_care_plan_parental_prolonged_seizure_care,
        registration__management__individualised_care_plan_addresses_sudep=individualised_care_plan_addresses_sudep,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).sudep

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"BOTH \nindividualised_care_plan_parental_prolonged_seizure_care\nindividualised_care_plan_addresses_sudep are True but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        reason = 'individualised_care_plan_parental_prolonged_seizure_care' if not individualised_care_plan_parental_prolonged_seizure_care else 'individualised_care_plan_addresses_sudep'
        assertion_message = f"{reason} is False but not failing"

    assert kpi_score == expected_score, assertion_message