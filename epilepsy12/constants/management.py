# Management

INFORMATION_TYPES=(
    (1, "Treatment goals"),
    (2, "Drug information leaflet"),
    (3, "Sodium Valproate Risks and benefits"),
    (4, "VNS option"),
    (5, "Surgery option"),
    (6, "Ketogenic option"),
    (999, "Other")
)

TRANSITION_TOPICS=(
    (1, "Driving"),
    (2, "Contraception"),
    (3, "Pregnancy"),
    (4, "Adherence"),
    (5, "Sleep hygiene"),
    (6, "Alcohol"),
    (7, "Recreational Drugs"),
    (8, "Career"),
    (9, "Bus pass"),
    (10, "Seen on own"),
    (11, "Self management"),
    (12, "Goal setting"),
    (13, "Ready"),
    (14, "Steady"),
    (15, "Go"),
    (16, "Hello"),
    (999, "Other")
)

IHP_STATUS=(
    (1, "No evidence"),
    (2, "Requested but no other evidence"),
    (3, "Possibly in place but uncertain"),
    (4, "Documented as in place but no copy of IHP"),
    (5, "Copy of the IHP within trust health record")
)

EHCP_STATUS=(
    (1, "No evidence"),
    (2, "Requested but no other evidence"),
    (3, "Possibly in place but uncertain"),
    (4, "Documented as in place but no copy of EHCP"),
    (5, "Copy of the EHCP within trust health record"),
    ("NA", "Not applicable to this patient")
)

EDUCATION_TYPE=(
    (1, "Consent to share health information with school"),
    (2, "Teacher generic epilepsy awareness"),
    (3, "IEP (individual education plan)"),
    (4, "Exam Provision"),
    (5, "School rescue medication plan"),
    (6, "School rescue medication training"),
    (999, "Other")
)