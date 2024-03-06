"""
Tests the Case model
"""

# Standard imports
import pytest
from datetime import date

# Third party imports

# RCPCH imports


@pytest.mark.django_db
def test_case_age_days_calculation(e12_case_factory):
    # Test that the age function works as expected

    e12Case = e12_case_factory(date_of_birth=date(2018, 5, 11))

    fixed_testing_date = date(2023, 6, 17)

    assert (
        e12Case.age_days(fixed_testing_date) == 1863
    ), "Incorrect age"  # "5 years, 1 month"


@pytest.mark.django_db
def test_case_age_calculation(e12_case_factory):
    # Test that the age function works as expected

    e12Case = e12_case_factory(date_of_birth=date(2018, 5, 11))

    fixed_testing_date = date(2023, 6, 17)

    assert (
        e12Case.age(fixed_testing_date) == "5 years, 1 month"
    ), "Incorrect calendar age"


@pytest.mark.django_db
def test_case_organisation_assignment(e12_case_factory):
    """Test that case has organisation(s) assigned"""
    e12Case = e12_case_factory()
    assert e12Case.organisations.count() > 0


@pytest.mark.django_db
def test_case_save_unknown_postcode(e12_case_factory):
    # Tests that the save method works as expected using one of the 'unknown' postcodes
    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=None)
    e12Case.postcode = "ZZ99 3CZ"
    e12Case.save()
    assert e12Case.index_of_multiple_deprivation_quintile is None


@pytest.mark.django_db
def test_case_save_postcode_obtain_imdq(e12_case_factory):
    # Tests that the save method works as expected using a known postcode IMD
    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=None)
    e12Case.postcode = "WC1X 8SH"  # RCPCH address
    e12Case.save()
    assert e12Case.index_of_multiple_deprivation_quintile == 4


@pytest.mark.django_db
def test_case_save_invalid_postcode(e12_case_factory):
    # Tests that the save method works as expected using an invalid postcode
    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=None)
    e12Case.postcode = "GARBAGE"
    e12Case.save()
    assert e12Case.postcode == "GARBAGE"
    assert e12Case.index_of_multiple_deprivation_quintile is None

@pytest.mark.django_db
def test_case_dont_overwrite_index_of_multiple_deprivation_quintile(e12_case_factory):
    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=5)

    e12Case.postcode = "WC1X 8SH"
    e12Case.save()
    assert e12Case.postcode == "WC1X 8SH"
    assert e12Case.index_of_multiple_deprivation_quintile is 5
