from dataclasses import dataclass, fields
from typing import Optional

# Common selectors

SECTION_STATUS_CHOICES = (
    (-1, "Not Set"),
    (0, "Not saved"),
    (5, "Disabled"),
    (10, "Complete"),
    (20, "Incomplete"),
    (30, "Errors"),
    (60, "TransferredIn"),
    (70, "TransferredOut"),
)

OPT_OUT = (("Y", "Yes"), ("N", "No"))

OPT_OUT_UNCERTAIN = (("Y", "Yes"), ("N", "No"), ("U", "Uncertain"))

CHECKED_STATUS = ((1, "Checked"), (2, "Unchecked"))

SEX_TYPE = (
    # This definition has been updated based on NHS standards
    # (cf https://www.datadictionary.nhs.uk/attributes/person_gender_code.html)
    (0, "Not Known"),
    (1, "Male"),
    (2, "Female"),
    (9, "Not Specified"),
)

CHRONICITY = ((1, "Acute"), (2, "Non-acute"), (3, "Don't know"))

DISORDER_SEVERITY = (
    ("Mil", "Mild"),
    ("Mod", "Moderate"),
    ("Sev", "Severe"),
    ("Pro", "Profound"),
)

DATE_ACCURACY = (
    ("Apx", "Approximate date"),
    ("Exc", "Exact date"),
    ("NK", "Not known"),
)


@dataclass
class DEPRIVATION_QUINTILES_DATACLASS:
    first: int = 1
    second: int = 2
    third: int = 3
    fourth: int = 4
    fifth: int = 5
    not_known: Optional[int] = None

    @property
    def deprivation_quintile_names(self):
        return [field.name for field in fields(self)]

    @property
    def deprivation_quintiles(self):
        return [getattr(self, field.name) for field in fields(self)]

    def deprivation_quintiles_int_display_map(self, deprivation_quintile):
        if deprivation_quintile is None:
            return 6

        return deprivation_quintile


DEPRIVATION_QUINTILES = DEPRIVATION_QUINTILES_DATACLASS()
