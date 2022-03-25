NEUROPSYCHIATRIC=(
    ("MoD", "Mood disorder"), 
    ("AxD", "Anxiety disorder"), 
    ("EmB", "Emotional/ behavioural"), 
    ("SHm", "Self harm"), 
    ("Oth", "Other")
)

DEVELOPMENTAL_BEHAVIOURAL=(
    ("CnD", "Conduct disorder"), 
    ("ODD", "Oppositional Defiant Disorder (ODD)")
)

NEURODEVELOPMENTAL=(
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

COMORBIDITIES = NEUROPSYCHIATRIC + DEVELOPMENTAL_BEHAVIOURAL + NEURODEVELOPMENTAL # TODO need to check if can concantenate lists in this way