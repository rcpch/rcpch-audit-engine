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

    ORGANISATION = "ODSCode"
    TRUST = "trust__ods_code"  #
    LOCAL_HEALTH_BOARD = "local_health_board__lhb22cd"  # __ods_code
    ICB = "integrated_care_board__icb23cd"  # __ODS_ICB_Code
    NHS_ENGLAND_REGION = "nhs_england_region__NHS_Region_Code"  # __nhser22cd
    OPEN_UK = "openuk_network__OPEN_UK_Network_Code"
    COUNTRY = "country"  # __ctry22cd
    NATIONAL = "country"  # __ctry22cd
