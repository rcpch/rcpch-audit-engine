from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .case import Case

class SeizureCause(TimeAndUserStampMixin):
    """
    This class records the cause of each seizure.
    It references the Episode class as each episode optionally has a cause.

    One Case can have multiple seizure causes
    """
    seizure_cause_main=models.CharField(
        max_length=3, 
        choices=EPILEPSY_CAUSES
    )
    seizure_cause_structural=models.CharField(
        max_length=3, 
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES
    )
    seizure_cause_genetic=models.CharField(
        max_length=3, 
        choices=EPILEPSY_GENETIC_CAUSE_TYPES
    )
    seizure_cause_chromosomal_abnormality=models.CharField( # would be good to pull in known chromosomal abnormalities 
        max_length=200
    )
    seizure_cause_gene_abnormality=models.CharField( # would be good to pull in known genetic abnormalities 
        max_length=3, 
        choices=EPILEPSY_GENE_DEFECTS
    )
    seizure_cause_gene_abnormality_snomed_code=models.CharField(max_length=50) # this is an extra field
    seizure_cause_genetic_other=models.CharField(max_length=250)
    seizure_cause_infectious=models.CharField(max_length=250)
    seizure_cause_infectious_snomed_code=models.CharField(max_length=250) # this is an extra field
    seizure_cause_metabolic=models.CharField(
        max_length=3, 
        choices=METABOLIC_CAUSES
    )
    seizure_cause_metabolic_other=models.CharField(max_length=250)
    seizure_cause_metabolic_snomed_code=models.CharField(max_length=250) # this is an extra field
    seizure_cause_immune=models.CharField(
        max_length=3, 
        choices=IMMUNE_CAUSES
    )
    seizure_cause_immune_antibody=models.CharField(
        max_length=3,
        choices=AUTOANTIBODIES
    )
    seizure_cause_immune_antibody_other=models.CharField(max_length=250)
    seizure_cause_immune_snomed_code=models.CharField(max_length=250) # this is an extra field

    #TODO this class needs to be referenced by Case