# Referral Process and Pathway Selectors

REFERRAL_STATUS=(
    (1, "Not requested"), 
    (2, "Requested and waiting"), 
    (3, "Obtained"), 
    (4, "Requested and did not attend"), 
    (5, "Requested and attempted but not achieved")
)

TRUST_VERIFICATION_STATUS=(
    ("REG", "Registered"), 
    ("VFD", "Trust Verified"), 
    ("NYV", "Not yet verified"), 
    ("EX1", "Excluded (Registration)"),
    ("EX2", "Excluded (Verification)"), 
    ("POO", "Patient opt out")
)

INPUT_STATUS=(
    ("a", "Ongoing input"), 
    ("b", "Previous input"), 
    ("c", "Uncertain"), 
    ("d", "None")
)

INPUT_REQUEST_STATUS=(
    (1, "Input not requested"),
    (2, "Input requested and waiting for input"),
    (3, "Input requested and input achieved"),
    (4, "Input requested and rejected"),
    (5, "Input requested and non-attended")
)

REFERRAL_SERVICES=(
    (1, "ED"), 
    (2, "GP"), 
    (3, "Health Visitor"), 
    (4, "Outpatient paediatrics"), 
    (5, "Inpatient paediatrics"), 
    (6, "PICU"), 
    (7, "Neonatal care"), 
    (8, "Other")
)

FOLLOW_UP_EPISODE_STATUS=(
    (1, "Discharged and transferred to another paediatric provider"), 
    (2, "Transferred to adult services"), 
    (3, "Discharged to GP because ongoing paediatric follow up not required"), 
    (7, "Discharged to GP because DNA/was not brought/Cancelled"), 
    (4, "Followed up by paediatrics but not because of epileptic non-epileptic or uncertain episodes"), 
    (5, "No ongoing follow up for other reason"), 
    (6, "Died")
)