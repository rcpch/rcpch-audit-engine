from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *
class NonEpilepsy(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about nonepilepsy features of episode.
    This class optionally references the Episode class as one episode can have one set of nonepilepsy features.
    """

    # TODO #20 NonEpilepsy Class to be reorganised to persist:
    # 1. SNOMED code
    # 2. readable title
    # if there is no snomed equivalent, default to the original picklists in the constants folder 

    nonepilepsy_type=models.IntegerField(
        "Type of nonepilepsy presentation.",
        choices=EPIS_TYPE
    )
    specific_nonepilepsy_diagnosis=models.CharField( # used in preference if known, but can be none
        "Specific nonepilepsy diagnosis if known",
        max_length=50
    )
    specific_nonepilepsy_diagnosis_snomed_code=models.CharField( # used in preference if known, but can be none
        "SNOMED-CT code for nonepilepsy diagnosis if known",
        max_length=3,
    )
    nonepilepsy_syncope=models.CharField(
        "Type of nonepileptic syncope.",
        max_length=3, 
        choices=NON_EPILEPTIC_SYNCOPES)
    nonepilepsy_syncope_snomed_code=models.CharField(
        "SNOMED-CT code for nonepilepsy syncope type",
        max_length=3
    )
    nonepilepsy_behavioural_symptoms=models.CharField(
        "Type of behavioural arrest described.",
        max_length=3, 
        choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS
    )
    nonepilepsy_behavioural_symptoms_snomed_code=models.CharField(
        "SNOMED-CT code for type of behavioural arrest described.",
        max_length=50, 
    )
    nonepilepsy_sleep=models.CharField(
        "Type of sleep symptoms reported.",
        max_length=3, 
        choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS
    )
    nonepilepsy_sleep_snomed_code=models.CharField(
        "SNOMED-CT code for type of sleep symptoms reported.",
        max_length=50 
    )
    nonepilepsy_paroxysmal=models.CharField(
        "Type of paroxysmal nonepileptic symptoms reported.",
        max_length=3, 
        choices=NON_EPILEPSY_PAROXYSMS
    )
    nonepilepsy_paroxysmal_snomed_code=models.CharField(
        "SNOMED-CT code for type of paroxysmal nonepileptic symptoms reported.",
        max_length=50, 
    )
    nonepilepsy_migraine=models.CharField(
        "Migraine semiology.",
        max_length=3,
        choices=MIGRAINES
    )
    nonepilepsy_migraine_snomed_code=models.CharField(
        "SNOMED-CT code for migraine semiology.",
        max_length=50
    )
    nonepilepsy_miscellaneous=models.CharField(
        "Other nonepileptic presentation if not previously specified.",
        max_length=3, 
        choices=EPIS_MISC)
    nonepilepsy_other=models.CharField(
        "Other nonepileptic presentation if not previously specified.",
        max_length=250
    )

    class Meta:
        ordering = ['nonepilepsy_type']
        verbose_name = 'Nonepilepsy'
        
    
    def __str__(self) -> str:
        return self.nonepilepsy_type