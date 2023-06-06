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

# ASSESSMENT=(
#         (0, "First paediatric assessment"),
#         (1, "First year of care"),
#         (2, "Second year of care"),
#         (3, "Third year of care"),
#         (4, "4th year of care"),
#         (5, "5th year of care"),
#         (6, "6th year of care"),
#         (7, "7th year of care"),
#         (8, "8th year of care"),
#         (9, "9th year of care"),
#         (10, "10th year of care")
#     )

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

DEPRIVATION_QUINTILES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (None, 6))
