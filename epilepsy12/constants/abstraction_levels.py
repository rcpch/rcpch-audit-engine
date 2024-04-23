from enum import Enum

ABSTRACTION_LEVELS = (
    ("organisation", "Organisation"),
    ("trust", "Trust/Local Health Board"),
    ("local_health_board", "Local Health Board"),
    ("icb", "Integrated Care Board"),
    ("open_uk", "OPEN UK network"),
    ("nhs_england_region", "NHS England Region"),
    ("country", "Country"),
    ("national", "National"),
)


class EnumAbstractionLevel(Enum):
    """These are all with respect to Organisation so queries would all require e.g. organisation__ODSCode"""

    ORGANISATION = "ods_code"
    TRUST = "trust__ods_code"
    LOCAL_HEALTH_BOARD = "local_health_board__boundary_identifier"
    ICB = "integrated_care_board__boundary_identifier"
    NHS_ENGLAND_REGION = "nhs_england_region__boundary_identifier"
    OPEN_UK = "openuk_network__boundary_identifier"
    COUNTRY = "country__boundary_identifier"
    NATIONAL = "country__name"
