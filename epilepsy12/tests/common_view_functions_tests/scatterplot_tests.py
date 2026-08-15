"""
Test the generate_dataframe_and_aggregated_distance_data_from_cases
"""

# python imports
import pytest

# Django imports
from django.contrib.gis.geos import Point

# E12 imports
from epilepsy12.common_view_functions import (
    generate_dataframe_and_aggregated_distance_data_from_cases,
    filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction,
)
from epilepsy12.tests.common_view_functions_tests.aggregate_by_tests.helpers import (
    _register_cases_in_organisation,
)
from epilepsy12.models import (
    Case,
    Organisation,
)


@pytest.mark.django_db
def test_generate_dataframe_and_aggregated_distance_data_from_cases(e12_case_factory):
    """Tests the generate_dataframe_and_aggregated_distance_data_from_cases fn returns correct count.

    In this test setup, we seed 10 cases with location_wgs84
    and distance_from_lead_organisation fields.

    Thus expected total count is 10.
    """

    # define constants
    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    GOSH.latitude = 51.525493
    GOSH.longitude = -0.127568
    MAX_DISTANCE_KM = 5

    points_within_5km = [
        {"latitude": 51.5518, "longitude": -0.1457, "distance": 3.19},
        {"latitude": 51.5025, "longitude": -0.1698, "distance": 3.89},
        {"latitude": 51.5679, "longitude": -0.1156, "distance": 4.79},
        {"latitude": 51.5417, "longitude": -0.0866, "distance": 3.37},
        {"latitude": 51.5169, "longitude": -0.1098, "distance": 1.56},
        {"latitude": 51.5178, "longitude": -0.0893, "distance": 2.79},
        {"latitude": 51.5558, "longitude": -0.1164, "distance": 3.46},
        {"latitude": 51.5303, "longitude": -0.1630, "distance": 2.52},
        {"latitude": 51.5014, "longitude": -0.1304, "distance": 2.69},
        {"latitude": 51.5391, "longitude": -0.1136, "distance": 1.80},
    ]

    # Create 10 cases with location_wgs84 and distance_from_lead_organisation
    _register_cases_in_organisation(["RP401"], e12_case_factory, n_cases=10)

    # Generate case locations within 5 km of GOSH
    # centre_point = Point(GOSH.longitude, GOSH.latitude)
    for count, case in enumerate(Case.objects.all()):
        case.location_wgs84 = Point(
            points_within_5km[count]["longitude"],
            points_within_5km[count]["latitude"],
        )
        case.save()

    filtered_cases = filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction(
        organisation=GOSH, cohort=6
    )

    cases_queryset, geo_df = generate_dataframe_and_aggregated_distance_data_from_cases(
        filtered_cases=filtered_cases
    )

    assert len(geo_df) == 10
    assert cases_queryset["max_distance_travelled_km"] == "4.79"
    assert cases_queryset["mean_distance_travelled_km"] == "3.00"
    assert cases_queryset["median_distance_travelled_km"] == "2.98"
    assert cases_queryset["std_distance_travelled_km"] == "0.96"
    assert cases_queryset["max_distance_travelled_mi"] == "2.97"
    assert cases_queryset["mean_distance_travelled_mi"] == "1.86"
    assert cases_queryset["median_distance_travelled_mi"] == "1.85"
    assert cases_queryset["std_distance_travelled_mi"] == "0.60"

    # Test with no location data
    for case in Case.objects.all():
        case.location_wgs84 = None
        case.save()

    filtered_cases = filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction(
        organisation=GOSH, cohort=6
    )

    assert (
        filtered_cases.count() == 0
    ), "Filtered cases length should be 0 cases as no location data"

    distances_object, geo_df = (
        generate_dataframe_and_aggregated_distance_data_from_cases(
            filtered_cases=filtered_cases
        )
    )

    assert (
        len(geo_df) == 0
    ), "Filtered geodataframe of cases with distances should be 0 cases as no location data"
    assert distances_object["max_distance_travelled_km"] == "~"
    assert distances_object["mean_distance_travelled_km"] == "~"
    assert distances_object["median_distance_travelled_km"] == "~"
    assert distances_object["std_distance_travelled_km"] == "~"
    assert distances_object["max_distance_travelled_mi"] == "~"
    assert distances_object["mean_distance_travelled_mi"] == "~"
    assert distances_object["median_distance_travelled_mi"] == "~"
    assert distances_object["std_distance_travelled_mi"] == "~"
