from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .case import Case

class SeizureCause(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records the cause of each seizure.
    It references the Episode class as each episode optionally has a cause.

    One Case can have multiple seizure causes
    """
    seizure_cause_main=models.CharField(
        "main identified cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_CAUSES
    )
    seizure_cause_main_snomed_code=models.CharField(
        "SNOMED-CT code for main identified cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_CAUSES
    )
    seizure_cause_structural=models.CharField(
        "main identified structural cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES
    )
    seizure_cause_structural_snomed_code=models.CharField(
        "SNOMED-CT code for main identified structural cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES
    )
    seizure_cause_genetic=models.CharField(
        "main identified genetic cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_GENETIC_CAUSE_TYPES
    )
    seizure_cause_gene_abnormality=models.CharField( # would be good to pull in known genetic abnormalities 
        "main identified gene abnormality cause of seizure(s)",
        max_length=3, 
        choices=EPILEPSY_GENE_DEFECTS
    )
    seizure_cause_genetic_other=models.CharField(
        "other identified genetic cause of seizure(s) not previously specified.",
        max_length=250
    )
    seizure_cause_gene_abnormality_snomed_code=models.CharField(
        "SNOMED-CT code for main identified genetic cause of seizure(s)",
        max_length=50
    )
    seizure_cause_chromosomal_abnormality=models.CharField( # would be good to pull in known chromosomal abnormalities 
        "main identified chromosomal cause of seizure(s)",
        max_length=200
    )
    
    seizure_cause_infectious=models.CharField(
        "main identified infectious cause of seizure(s)",
        max_length=250
    )
    seizure_cause_infectious_snomed_code=models.CharField(
        "SNOMED-CT code for main identified infectious cause of seizure(s)",
        max_length=250
    ) 
    seizure_cause_metabolic=models.CharField(
        "main identified metabolic cause of seizure(s)",
        max_length=3, 
        choices=METABOLIC_CAUSES
    )
    seizure_cause_metabolic_other=models.CharField(
        "other identified metabolic cause of seizure(s) not previously specified.",
        max_length=250
    )
    seizure_cause_metabolic_snomed_code=models.CharField(
        "SNOMED-CT code for other identified metabolic cause of seizure(s) not previously specified.",
        max_length=250
    )
    seizure_cause_immune=models.CharField(
        "main identified immune cause of seizure(s).",
        max_length=3, 
        choices=IMMUNE_CAUSES
    )
    seizure_cause_immune_antibody=models.CharField(
        "autoantibody identified as cause of seizure(s).",
        max_length=3,
        choices=AUTOANTIBODIES
    )
    seizure_cause_immune_antibody_other=models.CharField(
        "other identified antibody not previously specified causing seizure(s).",
        max_length=250
    )
    seizure_cause_immune_snomed_code=models.CharField(
        "SNOMED-CT code for main identified immune cause of seizure(s).",
        max_length=250
    )

    class Meta:
        verbose_name = 'Main cause of seizure(s)',
        verbose_name_plural="Main causes of seizure(s)"
        
    
    def __str__(self) -> str:
        return self.seizure_cause_main