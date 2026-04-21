"""
Tests the Case model
"""

# Standard imports
import pytest
from datetime import date
from unittest.mock import patch

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
def test_case_save_unknown_postcode_when_imd_not_none(e12_case_factory):
    # Tests that the save method works as expected using one of the 'unknown' postcodes
    e12Case = e12_case_factory(
        postcode="WC1X 8SH", index_of_multiple_deprivation_quintile=4
    )
    e12Case.postcode = "ZZ99 3CZ"
    e12Case.save()
    assert e12Case.index_of_multiple_deprivation_quintile is None


@pytest.mark.django_db
@patch("epilepsy12.models_folder.case.coordinates_for_postcode")
@patch("epilepsy12.models_folder.case.imd_for_postcode")
def test_case_save_postcode_obtain_imdq(
    mock_imd_for_postcode, mock_coordinates_for_postcode, e12_case_factory
):
    """
    Tests that the save method works as expected using a known postcode IMD.
    Mocks both the coordinates API and the IMD calculation API.
    """
    # Mock the coordinates API response
    mock_coordinates_for_postcode.return_value = (-0.1234, 51.5678)

    # Mock the IMD calculation API response to return quintile 4
    mock_imd_for_postcode.return_value = 4

    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=None)
    e12Case.postcode = "WC1X8SH"  # RCPCH address
    e12Case.save()

    # Verify both mocks were called
    mock_coordinates_for_postcode.assert_called_once_with(postcode="WC1X8SH")
    mock_imd_for_postcode.assert_called_once_with("WC1X8SH")

    # Verify the IMD was set correctly
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
@patch("epilepsy12.models_folder.case.coordinates_for_postcode")
@patch("epilepsy12.models_folder.case.imd_for_postcode")
def test_case_overwrite_index_of_multiple_deprivation_quintile(
    mock_imd_for_postcode, mock_coordinates_for_postcode, e12_case_factory
):
    e12Case = e12_case_factory(index_of_multiple_deprivation_quintile=5)

    # Mock the coordinates API response
    mock_coordinates_for_postcode.return_value = (-0.1234, 51.5678)

    # Mock the IMD calculation API response to return quintile 4
    mock_imd_for_postcode.return_value = 4

    e12Case.postcode = "WC1X 8SH"
    e12Case.save()
    # Verify both mocks were called
    mock_coordinates_for_postcode.assert_called_once_with(postcode="WC1X8SH")
    mock_imd_for_postcode.assert_called_once_with("WC1X8SH")
    assert e12Case.postcode == "WC1X8SH"
    assert e12Case.index_of_multiple_deprivation_quintile == 4
