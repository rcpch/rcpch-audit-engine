from enum import Enum

ABSTRACTION_LEVELS = (
    ("organisation", "Organisation"),
    ("trust", "Trust/Local Health Board"),
    ("icb", "Integrated Care Board"),
    ("open_uk", "OPEN UK region"),
    ("nhs_region", "NHS England Region"),
    ("country", "Country"),
    ("national", "National"),
)

class EnumAbstractionLevel(Enum):
    """These are all with respect to Organisation so queries would all require e.g. organisation__ODSCode"""
    ORGANISATION = 'ODSCode'
    TRUST = 'ParentOrganisation_ODSCode'
    ICB = 'integrated_care_board__ODS_ICB_Code'
    NHS_REGION = 'nhs_region__NHS_Region_Code'
    OPEN_UK = 'openuk_network__OPEN_UK_Network_Code'
    COUNTRY = 'ons_region__ons_country__Country_ONS_Code'
    NATIONAL = 'NATIONAL'