# Epilepsy Type Selectors

EPILEPSY_DIAGNOSIS_STATUS = (
    ("E", "Epileptic"),
    ("NE", "Non-epileptic"),
    ("U", "Uncertain")
)

DIAGNOSTIC_STATUS = (
    ("a", "The child has had an episode or episodes where one or more are considered epileptic"),
    ("b", "The child has had an episode or episodes that are considered non-epileptic only"),
    ("c", "The child has had an episode or episodes where there remains uncertainty whether episodes were epileptic or not.")
)

EPISODE_DEFINITION = (
    ("a", "This was a single episode"),
    ("b", "This was a cluster within 24 hours"),
    ("c", "These were 2 or more episodes more than 24 hours apart"),
)

EPIS_TYPE = (
    (1, "Syncope And Anoxic Seizures"),
    (2, "Behavioral Psychological And Psychiatric Disorders"),
    (3, "Sleep Related Conditions"),
    (4, "Paroxysmal Movement Disorders"),
    (5, "Migraine Associated Disorders"),
    (6, "Miscellaneous Events"),
    (7, "Other")
)

EPIL_TYPE_CHOICES = (
    (1, "Seizure diary"),
    (2, "Seizure types"),
    (3, "Syndrome type"),
    (4, "Prognosis"),
    (5, "Co-morbidities"),
    (6, "National Support Groups"),
    (999, "Other")
)
