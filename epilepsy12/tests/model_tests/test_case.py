"""
Tests the Case model
"""

# Standard imports
import pytest
from datetime import date

# Third party imports

# RCPCH imports
from epilepsy12.models import Case, Organisation

@pytest.fixture
@pytest.mark.django_db
def organisation():
    """
    Creates a minimal Organisation object instance for the test
    """
    return Organisation.objects.create(name="Test Hospital")


@pytest.mark.django_db
def test_case_creation_and_age(db):
    """
    Tests that a case can be created and that automatic functions work as expected
    """
    case = Case.objects.create()
    fixed_testing_date = date(2023, 6, 17)
    case.date_of_birth = date(2018, 5, 11)

    assert case.age(fixed_testing_date) == "5 years, 1 month"

    """
    Tests that an organisation can be assigned to a case
    """
    case.assign_organisation("Test Hospital")
    assert case.organisations.all()[0].name == "Test Hospital"