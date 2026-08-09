"""
Tests for the RCPCH NHS Organisations sync module
(``epilepsy12/general_functions/nhs_organisations_sync.py``).

These tests mock the API client functions (``list_organisations`` etc.) so
no network access is required, and exercise the upsert logic against the
real Django models (marked ``@pytest.mark.django_db``).

The fixtures build small API responses that exercise the key paths:
- creating a new entity
- updating an existing entity's fields
- wiring FKs on Organisation from nested relationship objects
- the empty-string case for relationships that don't apply (e.g. a Welsh
  organisation has ``trust: ""``)
"""

from datetime import date
from unittest.mock import patch

import pytest

from epilepsy12.general_functions import nhs_organisations_sync
from epilepsy12.models import (
    Country,
    IntegratedCareBoard,
    LocalHealthBoard,
    NHSEnglandRegion,
    OPENUKNetwork,
    Organisation,
    Trust,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


API_BASE_TRUST = {
    "ods_code": "RGT",
    "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FOUNDATION TRUST",
    "address_line_1": "CAMBRIDGE BIOMEDICAL CAMPUS",
    "address_line_2": "HILLS ROAD",
    "town": "CAMBRIDGE",
    "postcode": "CB2 0QQ",
    "country": "ENGLAND",
    "telephone": "",
    "website": "",
    "active": True,
    "published_at": "",
}

API_BASE_LHB = {
    "ods_code": "7A3",
    "name": "Swansea Bay University Health Board",
    "welsh_name": "Bwrdd Iechyd Prifysgol Bae Abertawe",
    "boundary_identifier": "W11000031",
    "bng_e": 266283,
    "bng_n": 198175,
    "long": -3.93489,
    "lat": 51.6664,
    "publication_date": "2022-04-14",
}

API_BASE_ICB = {
    "ods_code": "QUE",
    "name": "NHS Cambridgeshire and Peterborough Integrated Care Board",
    "boundary_identifier": "E54000056",
    "bng_e": 541305,
    "bng_n": 168583,
    "long": 0.029892,
    "lat": 51.3987,
    "publication_date": "2023-03-15",
}

API_BASE_REGION = {
    "region_code": "Y61",
    "name": "East of England",
    "boundary_identifier": "E40000007",
    "bng_e": 600000,
    "bng_n": 250000,
    "long": 0.1,
    "lat": 52.2,
    "publication_date": "2022-07-30",
}

API_BASE_COUNTRY = {
    "boundary_identifier": "E92000001",
    "name": "England",
    "welsh_name": "Lloegr",
    "bng_e": 394883,
    "bng_n": 370883,
    "long": -2.07811,
    "lat": 53.235,
    "globalid": "f6b76559-3626-49b8-b50b-bd15efcb0505",
}

API_BASE_NETWORK = {
    "boundary_identifier": "EPEN",
    "name": "Eastern Paediatric Epilepsy Network",
    "country": "England",
    "publication_date": "2022-12-08",
}

API_BASE_ORG = {
    "ods_code": "RGT01",
    "name": "ADDENBROOKE'S HOSPITAL",
    "website": "https://www.cuh.nhs.uk/",
    "address1": "HILLS ROAD",
    "address2": "",
    "address3": "",
    "telephone": "01223 245151",
    "city": "CAMBRIDGE",
    "county": "CAMBRIDGESHIRE",
    "latitude": 52.17513275,
    "longitude": 0.140753239,
    "postcode": "CB2 0QQ",
    "geocode_coordinates": {"type": "Point", "coordinates": [0.140753239, 52.17513275]},
    "active": True,
    "published_at": "",
    "trust": {"ods_code": "RGT", "name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"},
    "local_health_board": "",
    "integrated_care_board": {
        "boundary_identifier": "E54000056",
        "name": "NHS Cambridgeshire and Peterborough ICB",
        "ods_code": "QUE",
    },
    "nhs_england_region": {
        "region_code": "Y61",
        "name": "East of England",
        "boundary_identifier": "E40000007",
    },
    "openuk_network": {
        "name": "Eastern Paediatric Epilepsy Network",
        "boundary_identifier": "EPEN",
        "country": "England",
        "publication_date": "2022-12-08",
    },
    "london_borough": "",
    "country": {"boundary_identifier": "E92000001", "name": "England"},
}


# ---------------------------------------------------------------------------
# Trust sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_trusts_creates_new_trust():
    # Use a non-seeded ODS code to avoid colliding with seed data
    api_trust = {**API_BASE_TRUST, "ods_code": "RXX", "name": "TEST TRUST"}
    with patch.object(nhs_organisations_sync, "list_trusts", return_value=[api_trust]):
        result = nhs_organisations_sync.sync_trusts()

    trust = Trust.objects.get(ods_code="RXX")
    assert trust.name == "TEST TRUST"
    assert trust.town == "CAMBRIDGE"
    assert trust.active is True
    assert "RXX" in result


@pytest.mark.django_db
def test_sync_trusts_updates_existing_trust():
    # RGT is seeded; fetch it and verify the sync updates its name
    trust, _ = Trust.objects.get_or_create(
        ods_code="RGT", defaults={"name": "OLD NAME"}
    )
    if trust.name == "OLD NAME":
        # Was newly created by get_or_create, so the seed didn't have it
        pass
    with patch.object(nhs_organisations_sync, "list_trusts", return_value=[API_BASE_TRUST]):
        nhs_organisations_sync.sync_trusts()

    trust = Trust.objects.get(ods_code="RGT")
    assert trust.name == "CAMBRIDGE UNIVERSITY HOSPITALS NHS FOUNDATION TRUST"
    assert trust.town == "CAMBRIDGE"


# ---------------------------------------------------------------------------
# LocalHealthBoard sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_local_health_boards_creates_new_lhb():
    # Use a non-seeded ODS code
    api_lhb = {**API_BASE_LHB, "ods_code": "7XX", "name": "TEST LHB"}
    with patch.object(nhs_organisations_sync, "list_local_health_boards", return_value=[api_lhb]):
        nhs_organisations_sync.sync_local_health_boards()

    lhb = LocalHealthBoard.objects.get(ods_code="7XX")
    assert lhb.name == "TEST LHB"
    assert lhb.welsh_name == "Bwrdd Iechyd Prifysgol Bae Abertawe"
    assert lhb.boundary_identifier == "W11000031"


# ---------------------------------------------------------------------------
# IntegratedCareBoard sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_integrated_care_boards_creates_new_icb():
    # Use a non-seeded ODS code
    api_icb = {**API_BASE_ICB, "ods_code": "QXX", "name": "TEST ICB"}
    with patch.object(nhs_organisations_sync, "list_integrated_care_boards", return_value=[api_icb]):
        nhs_organisations_sync.sync_integrated_care_boards()

    icb = IntegratedCareBoard.objects.get(ods_code="QXX")
    assert icb.name == "TEST ICB"
    assert icb.boundary_identifier == "E54000056"


# ---------------------------------------------------------------------------
# NHSEnglandRegion sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_nhs_england_regions_creates_new_region():
    # Use a non-seeded region code
    api_region = {**API_BASE_REGION, "region_code": "YXX", "name": "Test Region"}
    with patch.object(nhs_organisations_sync, "list_nhs_england_regions", return_value=[api_region]):
        nhs_organisations_sync.sync_nhs_england_regions()

    region = NHSEnglandRegion.objects.get(region_code="YXX")
    assert region.name == "Test Region"
    assert region.boundary_identifier == "E40000007"


# ---------------------------------------------------------------------------
# Country sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_countries_creates_new_country_without_geom():
    # Use a non-seeded boundary identifier
    api_country = {**API_BASE_COUNTRY, "boundary_identifier": "E99999999", "name": "Test Country"}
    with patch.object(nhs_organisations_sync, "list_countries", return_value=[api_country]):
        nhs_organisations_sync.sync_countries()

    country = Country.objects.get(boundary_identifier="E99999999")
    assert country.name == "Test Country"
    assert country.welsh_name == "Lloegr"
    assert country.globalid == "f6b76559-3626-49b8-b50b-bd15efcb0505"


# ---------------------------------------------------------------------------
# OPENUKNetwork sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_openuk_networks_creates_new_network():
    # Use a non-seeded boundary identifier
    api_network = {**API_BASE_NETWORK, "boundary_identifier": "TEST", "name": "Test Network"}
    with patch.object(nhs_organisations_sync, "list_openuk_networks", return_value=[api_network]):
        nhs_organisations_sync.sync_openuk_networks()

    network = OPENUKNetwork.objects.get(boundary_identifier="TEST")
    assert network.name == "Test Network"
    assert network.country == "England"
    assert network.publication_date == date(2022, 12, 8)


# ---------------------------------------------------------------------------
# Organisation sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_organisations_creates_org_with_all_fks_wired():
    # Use a non-seeded ODS code to avoid colliding with seed data
    api_org = {**API_BASE_ORG, "ods_code": "RXX01", "name": "TEST HOSPITAL"}
    # Pre-populate parent entities (using non-seeded codes where needed)
    trust, _ = Trust.objects.get_or_create(
        ods_code="RGT",
        defaults={"name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"},
    )
    icb, _ = IntegratedCareBoard.objects.get_or_create(
        ods_code="QUE",
        defaults={
            "name": "NHS Cambridgeshire and Peterborough ICB",
            "boundary_identifier": "E54000056",
            "bng_e": 541305,
            "bng_n": 168583,
            "long": 0.029892,
            "lat": 51.3987,
        },
    )
    region, _ = NHSEnglandRegion.objects.get_or_create(
        region_code="Y61",
        defaults={
            "name": "East of England",
            "boundary_identifier": "E40000007",
            "bng_e": 600000,
            "bng_n": 250000,
            "long": 0.1,
            "lat": 52.2,
        },
    )
    country, _ = Country.objects.get_or_create(
        boundary_identifier="E92000001",
        defaults={"name": "England"},
    )
    network, _ = OPENUKNetwork.objects.get_or_create(
        boundary_identifier="EPEN",
        defaults={
            "name": "Eastern Paediatric Epilepsy Network",
            "country": "England",
        },
    )

    with patch.object(nhs_organisations_sync, "list_organisations", return_value=[api_org]):
        count = nhs_organisations_sync.sync_organisations(
            trusts_by_ods_code={"RGT": trust},
            icbs_by_ods_code={"QUE": icb},
            regions_by_code={"Y61": region},
            countries_by_boundary_id={"E92000001": country},
            networks_by_boundary_id={"EPEN": network},
        )

    assert count == 1
    org = Organisation.objects.get(ods_code="RXX01")
    assert org.name == "TEST HOSPITAL"
    assert org.trust == trust
    assert org.integrated_care_board == icb
    assert org.nhs_england_region == region
    assert org.country == country
    assert org.openuk_network == network
    assert org.local_health_board is None  # Welsh orgs have trust: ""
    assert org.latitude == 52.17513275
    assert org.postcode == "CB2 0QQ"


@pytest.mark.django_db
def test_sync_organisations_handles_empty_string_relationships():
    """A Welsh organisation has trust: "" and local_health_board populated."""
    # Use a non-seeded ODS code
    lhb, _ = LocalHealthBoard.objects.get_or_create(
        ods_code="7A3",
        defaults={
            "name": "Swansea Bay University Health Board",
            "welsh_name": "Bwrdd Iechyd Prifysgol Bae Abertawe",
            "boundary_identifier": "W11000031",
            "bng_e": 266283,
            "bng_n": 198175,
            "long": -3.93489,
            "lat": 51.6664,
        },
    )
    country, _ = Country.objects.get_or_create(
        boundary_identifier="W92000004",
        defaults={"name": "Wales"},
    )

    welsh_org = {
        "ods_code": "7A3XX",
        "name": "TEST WELSH HOSPITAL",
        "website": "",
        "address1": "MORRISTON HOSPITAL",
        "address2": "",
        "address3": "",
        "telephone": "",
        "city": "SWANSEA",
        "county": "",
        "latitude": 51.65,
        "longitude": -3.95,
        "postcode": "SA6 6NL",
        "geocode_coordinates": "",
        "active": True,
        "published_at": "",
        "trust": "",
        "local_health_board": {"ods_code": "7A3", "name": "Swansea Bay UHB"},
        "integrated_care_board": "",
        "nhs_england_region": "",
        "openuk_network": "",
        "london_borough": "",
        "country": {"boundary_identifier": "W92000004", "name": "Wales"},
    }

    with patch.object(nhs_organisations_sync, "list_organisations", return_value=[welsh_org]):
        nhs_organisations_sync.sync_organisations(
            lhbs_by_ods_code={"7A3": lhb},
            countries_by_boundary_id={"W92000004": country},
        )

    org = Organisation.objects.get(ods_code="7A3XX")
    assert org.local_health_board == lhb
    assert org.trust is None
    assert org.integrated_care_board is None
    assert org.nhs_england_region is None
    assert org.openuk_network is None
    assert org.country == country


@pytest.mark.django_db
def test_sync_organisations_updates_existing_org():
    # RGT01 is seeded; update its name via the sync
    org, _ = Organisation.objects.get_or_create(
        ods_code="RGT01", defaults={"name": "OLD NAME"}
    )
    trust, _ = Trust.objects.get_or_create(
        ods_code="RGT",
        defaults={"name": "CAMBRIDGE UNIVERSITY HOSPITALS NHS FT"},
    )

    with patch.object(nhs_organisations_sync, "list_organisations", return_value=[API_BASE_ORG]):
        nhs_organisations_sync.sync_organisations(trusts_by_ods_code={"RGT": trust})

    org = Organisation.objects.get(ods_code="RGT01")
    assert org.name == "ADDENBROOKE'S HOSPITAL"
    assert org.trust == trust


@pytest.mark.django_db
def test_sync_organisations_skips_org_with_no_ods_code():
    bad_org = {"name": "NO ODS CODE", "ods_code": ""}
    with patch.object(nhs_organisations_sync, "list_organisations", return_value=[bad_org]):
        count = nhs_organisations_sync.sync_organisations()

    assert count == 0
    assert not Organisation.objects.filter(name="NO ODS CODE").exists()


# ---------------------------------------------------------------------------
# sync_current_state (top-level)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_current_state_syncs_all_entities_in_transaction():
    # Use non-seeded codes to avoid colliding with seed data
    api_trust = {**API_BASE_TRUST, "ods_code": "RXX"}
    api_org = {**API_BASE_ORG, "ods_code": "RXX01", "trust": {"ods_code": "RXX", "name": "TEST TRUST"}}
    with patch.object(nhs_organisations_sync, "list_trusts", return_value=[api_trust]), \
         patch.object(nhs_organisations_sync, "list_local_health_boards", return_value=[API_BASE_LHB]), \
         patch.object(nhs_organisations_sync, "list_integrated_care_boards", return_value=[API_BASE_ICB]), \
         patch.object(nhs_organisations_sync, "list_nhs_england_regions", return_value=[API_BASE_REGION]), \
         patch.object(nhs_organisations_sync, "list_countries", return_value=[API_BASE_COUNTRY]), \
         patch.object(nhs_organisations_sync, "list_openuk_networks", return_value=[API_BASE_NETWORK]), \
         patch.object(nhs_organisations_sync, "list_organisations", return_value=[api_org]):
        result = nhs_organisations_sync.sync_current_state()

    assert result["trusts"] == 1
    assert result["local_health_boards"] == 1
    assert result["integrated_care_boards"] == 1
    assert result["nhs_england_regions"] == 1
    assert result["countries"] == 1
    assert result["openuk_networks"] == 1
    assert result["organisations"] == 1

    # Verify the organisation has its FKs wired up
    org = Organisation.objects.get(ods_code="RXX01")
    assert org.trust.ods_code == "RXX"
    assert org.integrated_care_board.ods_code == "QUE"
    assert org.nhs_england_region.region_code == "Y61"
    assert org.country.boundary_identifier == "E92000001"
    assert org.openuk_network.boundary_identifier == "EPEN"


# ---------------------------------------------------------------------------
# Truncation safeguard
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_trusts_truncates_oversized_name():
    """If the API returns a name longer than the field's max_length, the sync
    truncates it and logs a warning rather than crashing with a DataError."""
    # Trust.name has max_length=255 (widened in migration 0066).
    # To test truncation, we patch the field's max_length down to 50.
    from unittest.mock import PropertyMock

    trust_field = Trust._meta.get_field("name")
    original_max_length = trust_field.max_length
    trust_field.max_length = 50

    long_name = "A" * 200  # 200 chars, exceeds the patched max_length of 50
    api_trust = {**API_BASE_TRUST, "ods_code": "RYY", "name": long_name}

    try:
        with patch.object(nhs_organisations_sync, "list_trusts", return_value=[api_trust]):
            nhs_organisations_sync.sync_trusts()

        trust = Trust.objects.get(ods_code="RYY")
        assert len(trust.name) == 50
        assert trust.name == "A" * 50
    finally:
        trust_field.max_length = original_max_length