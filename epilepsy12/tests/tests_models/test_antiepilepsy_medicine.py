import pytest
from datetime import date
from django.forms import ValidationError
from epilepsy12.models import AntiEpilepsyMedicine, Management, MedicineEntity, Registration


@pytest.fixture
@pytest.mark.django_db
def registration():
    """
    Creates a minimal Registration object instance for the test
    """
    return Registration.objects.create()


@pytest.fixture
@pytest.mark.django_db
def management(registration):
    """
    Creates a minimal Management object instance for the test
    """
    return Management.objects.create(registration=registration)


@pytest.fixture
@pytest.mark.django_db
def medicine_entity():
    """
    Creates a minimal MedicineEntity object instance for the test
    """
    return MedicineEntity.objects.create(medicine_name='Test Medicine')


@pytest.mark.django_db
def test_length_of_treatment(management, medicine_entity):
    # Test when both start date and stop date are provided
    medicine = AntiEpilepsyMedicine.objects.create(
        management=management,
        medicine_entity=medicine_entity,
        antiepilepsy_medicine_start_date=date(2023, 1, 1),
        antiepilepsy_medicine_stop_date=date(2023, 1, 10)
    )
    assert medicine.length_of_treatment == '9 days'

    # Test when start date and stop date are the same
    medicine.antiepilepsy_medicine_start_date = date(2023, 2, 1)
    medicine.antiepilepsy_medicine_stop_date = date(2023, 2, 1)
    with pytest.raises(Exception):
        medicine.length_of_treatment

    # Test when stop date is before start date
    medicine.antiepilepsy_medicine_start_date = date(2023, 3, 1)
    medicine.antiepilepsy_medicine_stop_date = date(2023, 2, 1)
    with pytest.raises(ValidationError):
        medicine.clean()
