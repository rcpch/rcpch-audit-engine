from datetime import date

import pytest

from dateutil.relativedelta import relativedelta

from ..models import Organisation
from ..kpi import download_kpi_summary_as_csv
from ..common_view_functions.calculate_kpis import calculate_kpis
from ..common_view_functions.aggregate_by import update_all_kpi_agg_models


@pytest.mark.django_db
def test_remove_jersey_patients_from_kpi_export(
    e12_case_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    jersey_org = Organisation.objects.filter(
        country__name="Jersey"
    ).first()

    # Jersey is part of SWIPE but we still want to exclude it from the export
    jersey_openuk_network = jersey_org.openuk_network

    english_org = Organisation.objects.filter(
        country__name="England"
    ).exclude(
        openuk_network=jersey_openuk_network
    ).first()

    english_openuk_network = english_org.openuk_network

    assert jersey_openuk_network != english_openuk_network

    english_case = e12_case_factory(
        date_of_birth=date(2013, 1, 1),
        # Must have completed first year of care
        registration__first_paediatric_assessment_date=date(2013, 1, 1) + relativedelta(years=10),
        organisations__organisation=english_org,
        # pass KPI 10
        registration__management__individualised_care_plan_in_place=True,
        registration__management__individualised_care_plan_includes_ehcp=True,
    )

    calculate_kpis(english_case.registration)
    update_all_kpi_agg_models(organisation=english_org, cohort=english_case.registration.cohort, open_access=False)

    jersey_case = e12_case_factory(
        date_of_birth=date(2013, 1, 1),
        # Must have completed first year of care
        registration__first_paediatric_assessment_date=date(2013, 1, 1) + relativedelta(years=10),
        organisations__organisation=jersey_org,
        # pass KPI 10
        registration__management__individualised_care_plan_in_place=True,
        registration__management__individualised_care_plan_includes_ehcp=True,
    )

    calculate_kpis(jersey_case.registration)
    update_all_kpi_agg_models(organisation=jersey_org, cohort=english_case.registration.cohort, open_access=False)

    assert english_case.registration.cohort == jersey_case.registration.cohort

    (
        country_df,
        trust_hb_df,
        icb_df,
        region_df,
        network_df,
        national_df,
        reference_df,
        trust_totals_df,
        local_health_board_totals_df,
        icb_totals_df,
        nhs_england_region_totals_df,
        openuk_network_totals_df,
        country_totals_df,
    ) = download_kpi_summary_as_csv(cohort=english_case.registration.cohort)

    countries = set(country_df["Country"])
    assert "England" in countries
    assert "Jersey" not in countries

    # Check Jersey patient isn't accidentally included in England
    english_df = country_df.loc[country_df["Country"] == "England"]
    english_kpi_10_row = english_df.loc[english_df["Measure"] == "10. School Individual Health Care Plan"].iloc[0]

    assert english_kpi_10_row["Numerator"] == 1
    assert english_kpi_10_row["Denominator"] == 1

    countries = set(country_totals_df["Name"])
    assert "England" in countries
    assert "Jersey" not in countries

    # Check Jersey patient isn't accidentally included in the other countries
    english_df = country_totals_df.loc[country_totals_df["Name"] == "England"]
    welsh_df = country_totals_df.loc[country_totals_df["Name"] == "Wales"]

    assert english_df["All Registered Cases"].iloc[0] == 1
    assert english_df["All Cases"].iloc[0] == 1

    assert welsh_df["All Registered Cases"].iloc[0] == 0
    assert welsh_df["All Cases"].iloc[0] == 0

    # Check "National_level" does not include Jersey
    # The names of the sheet and the NationalKPIAggregation model are confusing because they come from before we added
    # Jersey. They really mean "England and Wales", as per the row name in the sheet.
    national_df = national_df.loc[national_df["Measure"] == "10. School Individual Health Care Plan"].iloc[0]
    assert national_df["Numerator"] == 1
    assert national_df["Denominator"] == 1

    # Jersey is in an Open UK Network (SWIPE) so we need to check it's excluded from that as well
    networks = set(network_df["Network"])
    assert jersey_openuk_network.boundary_identifier not in networks

    # Triple check the other case is in their (different) Open UK Network
    network_df = network_df.loc[network_df["Network"] == english_openuk_network.boundary_identifier]
    network_kpi_10_row = network_df.loc[network_df["Measure"] == "10. School Individual Health Care Plan"].iloc[0]

    assert network_kpi_10_row["Numerator"] == 1
    assert network_kpi_10_row["Denominator"] == 1