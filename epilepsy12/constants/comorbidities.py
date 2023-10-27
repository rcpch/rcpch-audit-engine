NEUROPSYCHIATRIC = (
    ("AxD", "Anxiety disorder"),
    ("EmB", "Emotional/ behavioural"),
    ("MoD", "Mood disorder"),
    ("SHm", "Self harm"),
    ("Oth", "Other")
)

DEVELOPMENTAL_BEHAVIOURAL = (
    ("CnD", "Conduct disorder"),
    ("ODD", "Oppositional Defiant Disorder (ODD)")
)

NEURODEVELOPMENTAL = (
    ("ASD", "Autistic spectrum disorder"),
    ("CeP", "Cerebral palsy"),
    ("NDC", "Neurodegenerative disease or condition"),
    ("ChD", "An identified chromosomal disorder with a neurological or developmental component"),
    ("ADH", "Attention deficit hyperactivity disorder"),
    ("Int", "intellectual disability/global development delay/'learning disability'"),
    ("Dsp", "dyspraxia"),
    ("Dsl", "dyslexia"),
    ("SDo", "speech disorder"),
    ("Oth", "other learning difficulty")
)

COMORBIDITIES = NEUROPSYCHIATRIC + DEVELOPMENTAL_BEHAVIOURAL + \
    NEURODEVELOPMENTAL  # TODO need to check if can concantenate lists in this way


COLIN_EDIT_SNOMED_NEURODISABILITY_REFSET = [
    "Attention deficit hyperactivity disorder", # (MBD - Minimal brain disorder),
    "Cerebral palsy", # (Cerebral palsy),
    "Conductive hearing loss", # (Conductive deafness),
    "DCD - developmental coordination disorder", # (Developmental dyspraxia),
    "Developmental language disorder", # (Developmental language disorder),
    "Developmental speech disorder", # (Developmental speech disorder, NOS),
    "Disorder of fluency", # (Disorder of fluency),
    "Dyscalculia", # (Dyscalculia),
    "Dysgraphia", # (Dysgraphia),
    "Dyslexia ", #(Specific reading difficulty),
    "Hereditary spastic paraplegia", # (Strumpell disease"),
    "Hydrocephalus", # (Hydrocephalus"),
    "Migraine", # (Migraine),
    "Moderate binocular visual impairment", # (Moderate visual impairment, binocular),
    "Movement disorder", # (Movement disorder),
    "Oppositional defiant disorder", # (Oppositional defiant disorder),
    "Sensorineural hearing loss", # (Perceptive deafness, NOS),
    "Sleep disorder", # (Sleep disorder, NOS),
    "Speech and language developmental delay", # (Speech and language developmental delay),
    "Tic disorder" # (Habit disorder)
]