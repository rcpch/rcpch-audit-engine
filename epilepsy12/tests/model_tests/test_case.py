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
def case(db):
    """
    Creates a Case object to test
    """
    return Case.objects.create()


@pytest.fixture
@pytest.mark.django_db
def organisation(db):
    # Gets an Organisation object to assign to Case
    return Organisation.objects.get(ODSCode="RP401")


@pytest.mark.django_db
def test_case_age_calculation(db, case, organisation):
    # Test that the age function works as expected
    fixed_testing_date = date(2023, 6, 17)
    case.date_of_birth = date(2018, 5, 11)

    assert case.age(fixed_testing_date) == "5 years, 1 month"


@pytest.mark.django_db
def test_case_organisation_assignment(db, case, organisation):
    # Tests that an organisation can be assigned to a case
    case.organisation = organisation
    assert case.organisation.ODSCode == "RP401"


@pytest.mark.django_db
def test_case_save_unknown_postcode(db, case, organisation):
    # Tests that the save method works as expected using one of the 'unknown' postcodes
    case.postcode = "ZZ99 3CZ"
    case.save()
    assert case.index_of_multiple_deprivation_quintile is None


@pytest.mark.django_db
def test_case_save_postcode_obtain_imdq(db, case, organisation):
    # Tests that the save method works as expected using a known postcode IMD
    case.postcode = "WC1X 8SH"  # RCPCH address
    case.save()
    assert case.index_of_multiple_deprivation_quintile == 4


@pytest.mark.django_db
def test_case_save_invalid_postcode(db, case, organisation):
    # Tests that the save method works as expected using an invalid postcode
    case.postcode = "GARBAGE"
    case.save()
    assert case.postcode == "GARBAGE"
    assert case.index_of_multiple_deprivation_quintile is None
