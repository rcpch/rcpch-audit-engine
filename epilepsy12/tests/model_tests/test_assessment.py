import pytest
from datetime import date
from epilepsy12.models import Assessment, Registration


@pytest.fixture
@pytest.mark.django_db
def registration():
    """
    Creates a minimal Registration object instance for the test
    """
    return Registration.objects.create()


# The following tests check if the calculated wait times for each service are correct.
# They are all using the same function behind the scenes.


@pytest.mark.django_db
def test_consultant_paediatrician_wait_1_week(db, registration):
    # Create an Assessment object with referral and input dates for a consultant paediatrician
    assessment = Assessment.objects.create(
        registration=registration,
        consultant_paediatrician_referral_date=date(2022, 1, 1),
        consultant_paediatrician_input_date=date(2022, 1, 10),
    )

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "1 week"


@pytest.mark.django_db
def test_consultant_paediatrician_wait_2_weeks(db, registration):
    assessment = Assessment.objects.create(
        registration=registration,
        consultant_paediatrician_referral_date=date(2022, 1, 1),
        consultant_paediatrician_input_date=date(2022, 1, 15),
    )

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "2 weeks"


@pytest.mark.django_db
def test_paediatric_neurologist_wait(registration):
    # Create an Assessment object with referral and input dates for a paediatric neurologist
    assessment = Assessment.objects.create(
        registration=registration,
        paediatric_neurologist_referral_date=date(2022, 1, 1),
        paediatric_neurologist_input_date=date(2022, 1, 15),
    )

    # Check if the calculated wait time for the paediatric neurologist is correct
    assert assessment.paediatric_neurologist_wait() == "2 weeks"


@pytest.mark.django_db
def test_childrens_epilepsy_surgery_wait(registration):
    """
    Create an Assessment object with referral and input dates for a children's epilepsy surgery service
    """
    assessment = Assessment.objects.create(
        registration=registration,
        childrens_epilepsy_surgical_service_referral_date=date(2022, 1, 1),
        childrens_epilepsy_surgical_service_input_date=date(2023, 3, 22),
    )

    # Check if the calculated wait time for the children's epilepsy surgery service is correct
    assert assessment.childrens_epilepsy_surgery_wait() == "3 weeks"


@pytest.mark.django_db
def test_epilepsy_nurse_specialist_wait(registration):
    """
    Create an Assessment object with referral and input dates for an epilepsy nurse specialist
    """
    assessment = Assessment.objects.create(
        registration=registration,
        epilepsy_specialist_nurse_referral_date=date(2022, 1, 1),
        epilepsy_specialist_nurse_input_date=date(2022, 1, 29),
    )

    # Check if the calculated wait time for the epilepsy nurse specialist is correct
    assert assessment.epilepsy_nurse_specialist_wait() == "4 weeks"
