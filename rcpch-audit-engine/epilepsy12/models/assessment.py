from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .antiepilepsy_drug import AntiEpilepsyDrug
from .electroclinical_syndrome import ElectroClinicalSyndrome
from .investigations import Investigations
from .nonepilepsy import NonEpilepsy
from .registration import Registration
from .rescue_medicine import RescueMedicine
from .seizure_cause import SeizureCause

class Assessment(TimeAndUserStampMixin):
    """
    This class stores information on each assessment performed during the registration period.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """
    
    assessment_date=models.DateTimeField()
    has_an_aed_been_given=models.BooleanField(
        default=False
    )
    rescue_medication_prescribed=models.BooleanField(
        default=False, 
    )
    does_the_child_have_any_of_the_childrens_epilepsy_surgical_service_referral_criteria=models.BooleanField(
        default=False
    )
    consultant_paediatrician_referral_date=models.DateField() # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    consultant_paediatrician_input_date=models.DateField() # National guidance is that children should wait nolonger than x weeks
    paediatric_neurologist_referral_made=models.BooleanField(
        default=False
    )
    paediatric_neurologist_referral_date=models.DateField() # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    paediatric_neurologist_input_date=models.DateField() # National guidance is that children should wait nolonger than x weeks
    childrens_epilepsy_surgical_service_referral_date=models.DateField() # not required field
    childrens_epilepsy_surgical_service_input_date=models.DateField() # not required field
    were_any_of_the_epileptic_seizures_convulsive=models.BooleanField(
        default=False
    )
    prolonged_generalized_convulsive_seizures=models.CharField(
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    experienced_prolonged_focal_seizures=models.CharField(
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    has_an_aed_been_given=models.CharField( # this might be part of assessment or relate to episode
        max_length=2, 
        choices=OPT_OUT
    )
    paroxysmal_episode=models.CharField(
        max_length=1, 
        choices=OPT_OUT
    )
    registration = models.OneToOneField(
        Registration,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )

    # relationships
    antiepilepsy_drug=models.ManyToManyField(
        AntiEpilepsyDrug
    )
    electroclinical_syndrome=models.OneToOneField(
        ElectroClinicalSyndrome,
        on_delete=models.CASCADE,
        primary_key=True
    )
    investigations=models.OneToOneField(
        Investigations,
        on_delete=models.CASCADE,
        primary_key=True
    )
    rescue_medicine=models.ManyToManyField(
        RescueMedicine
    )
    seizure_cause=models.ManyToManyField(
        SeizureCause
    )
    nonepilepsy=models.OneToOneField(
        NonEpilepsy,
        on_delete=models.CASCADE,
        primary_key=True
    )



    #TODO #14 Class function to calculate cohort based on first paediatric assessment date
    # this creates a cohort number (integer) based on where in the year they are

    # TODO #15 Class function to create calculated field epilepsy_years based on current date and date of first seizure in years