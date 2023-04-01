# Django imports
from django.utils import timezone
import requests
from pprint import pprint

# E12 imports
from ...models import Organisation
from ...constants import INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES, NHS_ENGLAND_REGIONS, UK_ONS_REGIONS, OPEN_UK_NETWORKS
from ...constants import SWANSEA_BAY_UNIVERSITY_HEALTH_BOARD, ANEURAN_BEVAN_LOCAL_HEALTH_BOARD, BETSI_CADWALADR_UNIVERSITY_HEALTH_BOARD, CARDIFF_AND_VALE_HEALTH_BOARD, CWM_TAF_HEALTH_BOARD, HYWEL_DDA_LOCAL_HEALTH_BOARD, POWYS_TEACHING_LOCAL_HEALTH_BOARD, WALES_HOSPITALS


def add_codes_to_organisation(organisation: Organisation):
    """
    Adds ODS and ONS codes to organisation trust model instance
    """

    parent_codes = next(
        (item for item in INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES if item["ODS Trust Code"] == organisation.ParentODSCode), None)

    if parent_codes:
        print('Adding NHS England regions and local authorities....')
        organisation.NHSEnglandRegion = parent_codes["NHS England Region"]
        organisation.NHSEnglandRegionCode = parent_codes["NHS England Region Code"]

        organisation.ICBName = parent_codes["ICB Name"]
        organisation.ICBODSCode = parent_codes["ODS ICB Code"]
        organisation.ICBONSBoundaryCode = parent_codes["ONS ICB Boundary Code"]

        organisation.LocalAuthorityName = parent_codes["Local Authority"]
        organisation.LocalAuthorityODSCode = parent_codes["ODS LA Code"]
        organisation.SubICBName = parent_codes["Sub ICB Locations (formerly CCGs)"]
        organisation.SubICBODSCode = parent_codes["ODS Sub ICB Code"]

        organisation.Country = "England"

        # get the nhs region ONS code
        nhs_region = next(
            (item for item in NHS_ENGLAND_REGIONS if item["NHS_ENGLAND_REGION_CODE"] == parent_codes["NHS England Region Code"]), None)
        if nhs_region:
            print('Adding NHS England regions ONS codes....')
            organisation.NHSEnglandRegionONSCode = nhs_region["NHS_ENGLAND_REGION_ONS_CODE"]
        else:
            print(f'{organisation.ParentName} has no NHS Region.')

    else:
        print(f'{organisation.ParentName} has no ICB or Local Authority.')

    # get the OPEN UK Netwok names/codes and country
    open_uk_network = next(
        (item for item in OPEN_UK_NETWORKS if item["ods trust code"] == organisation.ParentODSCode), None)
    if open_uk_network:
        print('Adding OPEN UK regions and codes....')
        organisation.OPENUKNetworkCode = open_uk_network.get(
            "OPEN UK Network Code", None)
        organisation.OPENUKNetworkName = open_uk_network.get(
            "OPEN UK Network Name", None)
        organisation.Country = open_uk_network.get("country", None)
    else:
        print(f'{organisation.ParentName} has no OPEN UK Network Code.')

    # get the country codes
    country = next(
        (item for item in UK_ONS_REGIONS if item["Country_ONS_Name"] == organisation.Country), None)
    if country:
        organisation.CountryONSCode = country["Country_ONS_Code"]
        print('Adding country codes....')
    else:
        print(f'{organisation.ParentName} has no Country codes.')

    organisation.DateValid = timezone.now()

    organisation.save()
    print(
        f'{organisation.OrganisationName}({organisation.ParentName}) updated.')


def add_codes_to_all_organisations():
    """
    Retrospective function for organisations that have already been seeded to update with codes
    """

    organisations = Organisation.objects.all()
    for organisation in organisations:
        add_codes_to_organisation(organisation=organisation)


def create_wales_organisations_object():

    for organisation in WALES_HOSPITALS:
        organisation_name = organisation['location_name'].split()[0]
        print(organisation_name)
        ods_url = f'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations?Name={organisation_name}&Status=Active'

    try:
        response = requests.get(ods_url)
    except Exception as error:
        print(f"error: {error}")

    organisations = []
    if len(response.json()['Organisations']) > 0:
        organisations.append(response.json()['Organisations'])

    pprint(organisations)


def nhs_api_search():
    nhs_api = 'https://api.nhs.uk/service-search?api-version=2&search="NHS Sector", "HOS","Princess Royal University Hospital"&searchFields=OrganisationSubType, OrganisationTypeId, OrganisationName'


def create_welsh_organisation():
    ODS_WELSH_HOSPITALS = [
        {
            "Name": "CEFN COED HOSPITAL",
            "OrgId": "7A3FJ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA2 0GH",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3FJ",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "CEFN COED REGIONAL HQ",
            "OrgId": "RT4UY",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA2 0GP",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RT4UY",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "TY GARNGOCH (DAY HOSPITAL)",
            "OrgId": "7A3FK",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA4 4LH",
            "LastChangeDate": "2014-01-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3FK",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "GLANRHYD HOSPITAL",
            "OrgId": "7A3FA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF31 4LN",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3FA",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "GORSEINON HOSPITAL",
            "OrgId": "7A3EM",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA4 4UU",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3EM",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "MORRISTON HOSPITAL",
            "OrgId": "7A3C7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA6 6NL",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3C7",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "MAESTEG GENERAL HOSPITAL",
            "OrgId": "7A3B9",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF34 9PW",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3B9",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "NEATH PORT TALBOT HOSPITAL",
            "OrgId": "7A3CJ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA12 7BX",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3CJ",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "CUH AT PRINCESS OF WALES HOSPITAL",
            "OrgId": "RGT1Q",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CB6 1DN",
            "LastChangeDate": "2018-03-12",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RGT1Q",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL",
            "OrgId": "503PA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2018-06-13",
            "PrimaryRoleId": "RO222",
            "PrimaryRoleDescription": "LOCAL AUTHORITY SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/503PA",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL",
            "OrgId": "RP777",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2021-02-05",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RP777",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL",
            "OrgId": "RR857",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2021-02-04",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RR857",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL",
            "OrgId": "RY5AE",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2021-02-12",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RY5AE",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA, PRINCESS OF WALES HOSPITAL",
            "OrgId": "RJL30",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RJL30",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA, PRINCESS OF WALES HOSPITAL ELECTIVE SURGICAL HUB",
            "OrgId": "T9F5R",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2022-12-19",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/T9F5R",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL GRIMSBY",
            "OrgId": "RCU65",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2019-05-09",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RCU65",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "DIANA PRINCESS OF WALES HOSPITAL - GRIMSBY",
            "OrgId": "RWA06",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "DN33 2BA",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RWA06",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES COMMUNITY HOSPITAL",
            "OrgId": "RWP06",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "B61 0BB",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RWP06",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES HOSPITAL",
            "OrgId": "7A3B7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF31 1RQ",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3B7",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES HOSPITAL",
            "OrgId": "R1ACG",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "B61 0BB",
            "LastChangeDate": "2021-02-08",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/R1ACG",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES HOSPITAL",
            "OrgId": "RGN98",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CB6 1DN",
            "LastChangeDate": "2021-06-01",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RGN98",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES HOSPITAL",
            "OrgId": "RT1FD",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CB6 1DN",
            "LastChangeDate": "2021-02-04",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RT1FD",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "PRINCESS OF WALES HOSPITAL",
            "OrgId": "RYV03",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CB6 1DN",
            "LastChangeDate": "2021-02-04",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RYV03",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "SINGLETON HOSPITAL",
            "OrgId": "7A3C4",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA2 8QA",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3C4",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "TONNA DAY HOSPITAL",
            "OrgId": "7A3KB",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA11 3LX",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3KB",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "TONNA HOSPITAL",
            "OrgId": "7A3FL",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA11 3LX",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3FL",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "CIMLA HOSPITAL",
            "OrgId": "7A3DR",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA11 3SU",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3DR",
            "Region": "Swansea Bay University Health Board",
            "RegionCode": "W11000031"
        },
        {
            "Name": "CHEPSTOW COMMUNITY HOSPITAL",
            "OrgId": "7A6BJ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP16 5YX",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6BJ",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "LLANFRECHFA GRANGE HOSPITAL",
            "OrgId": "7A6G5",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP44 8YN",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6G5",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "MAINDIFF COURT HOSPITAL",
            "OrgId": "7A6FN",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP7 8NF",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6FN",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "HOMEWARD BOUND UNIT NEVILL HALL",
            "OrgId": "O9L6S",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP7 7EG",
            "LastChangeDate": "2022-11-24",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/O9L6S",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "NEVILL HALL CHILDRENS CENTRE",
            "OrgId": "7A623",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP7 7EG",
            "LastChangeDate": "2019-08-23",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A623",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "NEVILL HALL HOSPITAL",
            "OrgId": "7A6AM",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP7 7EG",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6AM",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "ROYAL GWENT HOSPITAL",
            "OrgId": "7A6AR",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP20 2UB",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6AR",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "ST CADOCS HOSPITAL",
            "OrgId": "7A6F7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP18 3XQ",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6F7",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "ST WOOLOS COMMUNITY",
            "OrgId": "7A6AT",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP20 4SZ",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6AT",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "YSBYTY ANEURIN BEVAN",
            "OrgId": "7A6AU",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP23 6GL",
            "LastChangeDate": "2021-05-10",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6AU",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "YSBYTY TRI CHWM",
            "OrgId": "7A6FR",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "NP23 6HA",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6FR",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "YSBYTY YSTRAD FAWR",
            "OrgId": "7A6AV",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF82 7EP",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A6AV",
            "Region": "Aneuran Bevan Local Health Board",
            "RegionCode": "W11000028"
        },
        {
            "Name": "FLINT COMMUNITY HOSPITAL",
            "OrgId": "7A1AA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH6 5HG",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AA",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "DEESIDE COMMUNITY HOSPITAL",
            "OrgId": "7A1CC",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH5 1XS",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1CC",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "CHIRK COMMUNITY HOSPITAL",
            "OrgId": "7A1A7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL14 5LN",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A7",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "HOLYWELL COMMUNITY HOSPITAL",
            "OrgId": "7A1AB",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH8 7TZ",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AB",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "MOLD COMMUNITY HOSPITAL",
            "OrgId": "7A1AD",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH7 1XG",
            "LastChangeDate": "2022-10-18",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AD",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "MOLD COMMUNITY HOSPITAL",
            "OrgId": "RL105",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH7 1XG",
            "LastChangeDate": "2021-02-05",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RL105",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "PENLEY HOSPITAL",
            "OrgId": "7A1D4",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 0AY",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1D4",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "WREXHAM MAELOR HOSPITAL",
            "OrgId": "7A1A4",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 7TD",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A4",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "WREXHAM MAELOR HOSPITAL",
            "OrgId": "R1DD4",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 7TD",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/R1DD4",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "WREXHAM MAELOR HOSPITAL",
            "OrgId": "RET32",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 7TD",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RET32",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "WREXHAM MAELOR HOSPITAL",
            "OrgId": "RJR65",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 7TD",
            "LastChangeDate": "2020-03-04",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RJR65",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "WREXHAM MAELOR HOSPITAL",
            "OrgId": "RL111",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL13 7TD",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RL111",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "BRYN BERYL HOSPITAL",
            "OrgId": "7A1AX",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL53 6TT",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AX",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "BRYN-Y-NEUADD HOSPITAL",
            "OrgId": "7A1GE",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL33 0HH",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1GE",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "CEFNI HOSPITAL",
            "OrgId": "7A1DD",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL77 7PP",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1DD",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "DOLGELLAU & BARMOUTH DISTRICT HOSPITAL SITE",
            "OrgId": "7A1AY",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL40 1NT",
            "LastChangeDate": "2013-07-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AY",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "DOLGELLAU SDP",
            "OrgId": "RT4W1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL40 1HA",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RT4W1",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "ERYRI HOSPITAL",
            "OrgId": "7A1DG",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL55 2YE",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1DG",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "CANOLFAN GOFFA FFESTINIOG",
            "OrgId": "7A1PL",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL41 3DW",
            "LastChangeDate": "2018-06-14",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1PL",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "LLANDUDNO GENERAL HOSPITAL SITE",
            "OrgId": "7A1AV",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL30 1LB",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AV",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "TYWYN & DISTRICT WAR MEMORIAL HOSPITAL SITE",
            "OrgId": "7A1B2",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL36 9HH",
            "LastChangeDate": "2012-05-15",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1B2",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "YSBYTY GWYNEDD",
            "OrgId": "7A1AU",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL57 2PW",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AU",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "ABERGELE HOSPITAL",
            "OrgId": "7A1A2",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL22 8DP",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A2",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "COLWYN BAY COMMUNITY HOSPITAL",
            "OrgId": "7A1A8",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL29 8AY",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A8",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "DENBIGH COMMUNITY HOSPITAL",
            "OrgId": "7A1A9",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL16 3ES",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A9",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "GLAN CLWYD HOSPITAL",
            "OrgId": "RL121",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL18 5UJ",
            "LastChangeDate": "2021-02-09",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RL121",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "YSBYTY PENRHOS STANLEY",
            "OrgId": "7A1DC",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL65 2QA",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1DC",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "LLANGOLLEN CLINIC",
            "OrgId": "7A1S1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL20 8HL",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1S1",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "NORTH WALES CANCER TREATMENT CENTRE",
            "OrgId": "7A1HD",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL18 5UJ",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1HD",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "PRESTATYN CLINIC",
            "OrgId": "7A1S4",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL19 9AA",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1S4",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "ROYAL ALEXANDRA HOSPITAL",
            "OrgId": "7A1A5",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL18 3AS",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1A5",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "RUTHIN COMMUNITY HOSPITAL",
            "OrgId": "7A1AF",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL15 1PS",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1AF",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "YSBYTY ALLTWEN",
            "OrgId": "7A1CA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LL49 9AQ",
            "LastChangeDate": "2022-10-18",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A1CA",
            "Region": "Betsi Cadwaladr University Health Board",
            "RegionCode": "W11000023"
        },
        {
            "Name": "LANSDOWNE CHILDRENS CENTRE CLINIC",
            "OrgId": "RX2V5",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "BN27 1NP",
            "LastChangeDate": "2021-07-21",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RX2V5",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "ROOKWOOD HOSPITAL",
            "OrgId": "7A4BX",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF5 2YN",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4BX",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "ST DAVID'S COMMUNITY HOSPITAL",
            "OrgId": "7A4FE",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF11 9XB",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4FE",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "UNIVERSITY HOSPITAL OF WALES",
            "OrgId": "7A4BV",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF14 4XW",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4BV",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "UNIVERSITY HOSPITAL OF WALES",
            "OrgId": "R2F2E",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF14 4XW",
            "LastChangeDate": "2020-12-10",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/R2F2E",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "UNIVERSITY HOSPITAL OF WALES",
            "OrgId": "RTH18",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "OX3 9DU",
            "LastChangeDate": "2019-05-10",
            "PrimaryRoleId": "RO198",
            "PrimaryRoleDescription": "NHS TRUST SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RTH18",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "NOAHS ARK CHILDRENS HOSPITAL FOR WALES",
            "OrgId": "7A4H1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF14 4XW",
            "LastChangeDate": "2016-07-21",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4H1",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "THE BARRY HOSPITAL",
            "OrgId": "7A4CH",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF62 8YH",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4CH",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "UNIVERSITY HOSPITAL LLANDOUGH",
            "OrgId": "7A4C1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF64 2XX",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A4C1",
            "Region": "Cardiff and Vale University Health Board",
            "RegionCode": "W11000029"
        },
        {
            "Name": "DEWI SANT HOSPITAL",
            "OrgId": "7A5DK",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF37 1LB",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5DK",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "YSBYTY CWM RHONDDA",
            "OrgId": "7A5CA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF40 2LX",
            "LastChangeDate": "2022-10-18",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5CA",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "YSBYTY CWM CYNON",
            "OrgId": "7A5HA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF45 4BZ",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5HA",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "PONTYPRIDD & DISTRICT HOSPITAL",
            "OrgId": "7A5BK",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF37 4AX",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5BK",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "PRINCE CHARLES HOSPITAL SITE",
            "OrgId": "7A5B3",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF47 9DT",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5B3",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "THE ROYAL GLAMORGAN HOSPITAL",
            "OrgId": "7A5B1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF72 8XR",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5B1",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "YSBYTY GEORGE THOMAS",
            "OrgId": "7A5DV",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF42 6YG",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A5DV",
            "Region": "Cwm Taf Morgannwg University Health Board",
            "RegionCode": "W11000030"
        },
        {
            "Name": "AMMAN VALLEY HOSPITAL",
            "OrgId": "7A2E1",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA18 2BQ",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2E1",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "BRONGLAIS GENERAL HOSPITAL",
            "OrgId": "7A2AJ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY23 1ER",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2AJ",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "BRYNTIRION INFANT WELFARE CLINIC",
            "OrgId": "7A3NC",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CF31 4EA",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A3NC",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "CARDIGAN HEALTH CENTRE",
            "OrgId": "7A2M7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA43 1EB",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2M7",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "CARDIGAN INTEGRATED CARE CENTRE",
            "OrgId": "7A2L7",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA43 1JX",
            "LastChangeDate": "2021-08-11",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2L7",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "LLANDOVERY HOSPITAL",
            "OrgId": "7A2AH",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA20 0LA",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2AH",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "MYNYDD ISA CLINIC",
            "OrgId": "7A122",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "CH7 6UH",
            "LastChangeDate": "2013-07-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A122",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "NEW TENBY COTTAGE HOSPITAL",
            "OrgId": "7A2JA",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA70 8AG",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2JA",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "TREGARON HOSPITAL",
            "OrgId": "7A2D8",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY25 6JP",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2D8",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "WEST WALES GENERAL HOSPITAL",
            "OrgId": "7A2AG",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA31 2AF",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2AG",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "WITHYBUSH GENERAL HOSPITAL",
            "OrgId": "7A2BL",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA61 2PZ",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2BL",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "WITHYBUSH HOSPITAL CHILD HEALTH SECTION",
            "OrgId": "7A2BM",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA61 2PZ",
            "LastChangeDate": "2014-10-15",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A2BM",
            "Region": "Hywel Dda Local Health Board",
            "RegionCode": "W11000025"
        },
        {
            "Name": "BRECONSHIRE WAR MEMORIAL HOSPITAL",
            "OrgId": "7A7BT",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LD3 7NS",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BT",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "BRODDYFI COMMUNITY HOSPITAL",
            "OrgId": "7A7BQ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY20 8AD",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BQ",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "BRONLLYS HOSPITAL",
            "OrgId": "7A7EH",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LD3 0LY",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7EH",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "BUILTH WELLS CLINIC",
            "OrgId": "7A73F",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LD2 3BA",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A73F",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "KNIGHTON HOSPITAL",
            "OrgId": "7A7EG",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LD7 1DF",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7EG",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "LLANDRINDOD WELLS HOSPITAL",
            "OrgId": "7A7BN",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "LD1 5HF",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BN",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "LLANIDLOES AND DISTRICT WAR MEMORIAL HOSPITAL",
            "OrgId": "7A7BP",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY18 6HF",
            "LastChangeDate": "2012-05-15",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BP",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "MONTGOMERYSHIRE COUNTY INFIRMARY",
            "OrgId": "7A7BR",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY16 2DW",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BR",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "VICTORIA MEMORIAL HOSPITAL",
            "OrgId": "7A7BS",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SY21 7DU",
            "LastChangeDate": "2021-01-28",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7BS",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        },
        {
            "Name": "YSTRADGYNLAIS COMMUNITY HOSPITAL",
            "OrgId": "7A7EJ",
            "Status": "Active",
            "OrgRecordClass": "RC2",
            "PostCode": "SA9 1AU",
            "LastChangeDate": "2013-05-08",
            "PrimaryRoleId": "RO148",
            "PrimaryRoleDescription": "LOCAL HEALTH BOARD SITE",
            "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/7A7EJ",
            "Region": "Powys Teaching Local Health Board",
            "RegionCode": "W11000024"
        }
    ]
    """














    Latitude
    Longitude


    OPENUKNetworkName
    OPENUKNetworkCode
    NHSEnglandRegion
    NHSEnglandRegionCode
    NHSEnglandRegionONSCode
    ICBName
    ICBODSCode
    ICBONSBoundaryCode
    LocalAuthorityName
    LocalAuthorityODSCode
    SubICBName
    SubICBODSCode

    DateValid
    """

    new_organisations = []
    for organisation in ODS_WELSH_HOSPITALS:
        ods_url = f'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{organisation["OrgId"]}'

        try:
            response = requests.get(ods_url)
        except Exception as error:
            print(f"error: {error}")

        location = response.json()["Organisation"]["GeoLoc"]["Location"]
        organisation = response.json()["Organisation"]

        new_organisation = {
            'OrganisationID': None,
            'OrganisationCode': organisation.get("OrgId", None),
            'OrganisationType': None,
            'SubType': None,
            'Sector': 'NHS Sector',
            'OrganisationStatus': 'Visible',
            'IsPimsManaged': None,
            'OrganisationName': organisation.get('Name', None),
            'Address1': location.get('AddrLn1', None),
            'Address2': location.get('AddrLn2'),
            'Address3': location.get('AddrLn3'),
            'City': location.get('Town'),
            'County': location.get('County'),
            'Postcode': location.get('PostCode'),
            'ParentODSCode': organisation.get("RegionCode"),
            'ParentName': organisation.get("Region"),
            'CountryONSCode': "W92000004",
            'Country': location.get('Country', None),
            'Phone': None,
            'Email': None,
            'Website': None,
            'Fax': None
        }

        new_organisations.append(new_organisation)
    pprint(new_organisations)
