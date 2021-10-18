# Epilepsy Causes

EPILEPSY_CAUSES=(
    ("Str", "Structural"), 
    ("Gen", "Genetic"), 
    ("Inf", "Infectious"), 
    ("Met", "Metabolic"), 
    ("Imm", "Immune"), 
    ("NK", "Not known")
)

EPILEPSY_STRUCTURAL_CAUSE_TYPES=(
    ("TbS", "Tuberous Sclerosis"), 
    ("StW", "Sturge Weber"), 
    ("FCD","Focal cortical dysplasia"), 
    ("HyH", "Hypothalamic Hamartoma"), 
    ("LGT","Low grade tumour"), 
    ("TuO","Tumour (other)"), 
    ("MCD", "Malformations of Cortical Development"), 
    ("Vas" , "Vascular (eg arterial ischaemic stroke venous ischaemia cerebral haemorrhage)"), 
    ("TBI", "Traumatic brain injury"), 
    ("NR", "Not required")
)

EPILEPSY_GENETIC_CAUSE_TYPES=(
    ("DrS","Dravet syndrome"), 
    ("GTD","Glucose Transporter Defect"), 
    ("AnS", "Angelman Syndrome"), 
    ("ReS", "Rett Syndrome"), 
    ("ChA", "Chromosomal abnormality"),
    ("GeA", "Gene abnormality")
)

EPILEPSY_GENE_DEFECTS=(
    ("UBE","UBE3A"), 
    ("GLU", "GLUT1"), 
    ("SLC", "SLC2A1"), 
    ("MEC", "MECP2"),
("SCN", "SCN1A"), 
    ("STX", "STXBP1"), 
    ("CDK", "CDKL5"), 
    ("KCN", "KCNQ2"), 
    ("SCN", "SCN2A"), 
    ("KCN", "KCNT1"), 
    ("ARX", "ARX"), 
    ("FOX", "FOXG1"), 
    ("PCD", "PCDH19"), 
    ("GRI", "GRIN2A"), 
    ("Oth", "Other")
)

METABOLIC_CAUSES=(
    ("Mit", "Mitochondrial disorder"), 
    ("Neu", "Neuronal Ceroid Lipofuscinosis (Batten Disease)"), 
    ("PPM", "Disorder of pyridoxine/pyridoxal phosphate metabolism"), 
    ("BiM", "Disorder of biotin metabolism"), 
    ("CrM", "Disorder of creatine metabolism"), 
    ("AmA", "Disorder of amino acid"), 
    ("UrA", "Disorder of urea cycle"), 
    ("PyP", "Disorder of pyrimidine and purine"), 
    ("Cho", "Disorder of cholesterol"), 
    ("Oth", "Other neurometabolic disorder")
)

IMMUNE_CAUSES=(
    ("RaE", "Rasmussen Encephalitis"), 
    ("AnM", "Antibody mediated")
)

AUTOANTIBODIES=(
    ("VGK", "VGKC"), 
    ("NMD", "NMDAR"), 
    ("GAD", "GAD"), 
    ("TPO", "TPO"), 
    ("MOG", "MOG"), 
    ("Oth", "Other")
)

ELECTROCLINICAL_SYNDROMES=(
    (46, "Autosomal dominant nocturnal frontal lobe epilepsy (ADNFLE)"), 
    (48, "Autosomal dominant partial epilepsy with auditory features)"), 
    (30, "Bathing epilepsy"), 
    (4,"(Benign) childhood epilepsy with centrotemporal spikes (BECTS) (benign rolandic epilepsy)"), 
    (16, "Benign familial neonatal seizures"), 
    (38, "Benign infantile seizures"), 
    (37, "(Benign) Myoclonic epilepsy in infancy"), 
    (21, "Benign neonatal seizures Benign non-familial neonatal seizures"), 
    (13, "Childhood absence epilepsy (CAE)"), 
    (27, "Childhood epilepsy with occipital paroxysms"), 
    (14, "Dravet syndrome (severe myoclonic epilepsy of/in infancy or SMEI)"), 
    (34, "Early myoclonic encephalopathy"), 
    (44, "Epilepsy with generalized tonic-clonic seizures only (Epilepsy with generalised tonic clonic seizures on awakening)"), 
    (41, "Epilepsy with myoclonic absences"), 
    (5, "Epilepsy with myoclonic astatic seizures (Doose syndrome) (Myoclonic astatic epilepsy)"), 
    (24, "Eyelid myoclonia with absences"), 
    (47, "Familial temporal lobe epilepsies"), 
    (32, "Familial focal epilepsy with variable foci"), 
    (10, "Frontal lobe epilepsy"), 
    (23, "Gelastic seizures due to hypothalamic hamartoma"), 
    (33, "Generalized Epilepsies with Febrile seizures plus (FS+)"), 
    (28, "Hemiconvulsion-hemiplegia syndrome"), 
    (29, "Hot water epilepsy"), 
    (17, "Idiopathic focal epilepsy of childhood"), 
    (12, "Juvenile absence epilepsy (JAE)"), 
    (11, "Juvenile myoclonic epilepsy (JME)"), 
    (40, "Late onset childhood occipital epilepsy (Gastaut type) (idiopathic childhood occipital epilepsy)"), 
    (42, "Lennox-Gastaut syndrome"), 
    (43, "Landau-Kleffner syndrome"), 
    (36, "Migrating partial (focal) seizures of infancy"), 
    (39, "Myoclonic encephalopathy in non-progressive disorders (myoclonic status in non-progressive encephalopathies)"), 
    (7, "Occipital lobe epilepsy"), 
    (35, "Ohtahara syndrome"), 
    (6, "Panayiotopoulos syndrome (Early onset (benign) childhood occipital epilepsy"), 
    (8, "Parietal lobe epilepsy"), 
    (25, "Perioral myoclonia with absences"), 
    (26, "Phantom absences"), 
    (19, "Primary reading epilepsy"), 
    (45, "Progressive myoclonus (myoclonic) epilepsies (PME)"), 
    (22, "Rasmussen's encephalitis (chronic progressive epilepsia partialis continua) (Kozhevnikov syndrome)"), 
    (31, "Reflex epilepsies"), 
    (20, "Startle epilepsy"), 
    (9, "Temporal lobe epilepsy"), 
    (18, "Visual sensitive epilepsies"), 
    (15, "West syndrome"), 
    (3, 'Unclassified syndrome'), 
    (1, "No epilepsy syndrome stated"), 
    ("O", "Other")
)
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