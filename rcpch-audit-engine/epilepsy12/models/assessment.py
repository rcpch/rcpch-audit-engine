from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .antiepilepsy_medicine import AntiEpilepsyMedicine
from .electroclinical_syndrome import ElectroClinicalSyndrome
from .investigations import Investigations
from .nonepilepsy import NonEpilepsy
from .registration import Registration
from .rescue_medicine import RescueMedicine
from .seizure_cause import SeizureCause

class Assessment(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class stores information on each assessment performed during the registration period.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """
    
    assessment_date=models.DateTimeField(
        "Date of assessment"
    )
    has_an_aed_been_given=models.BooleanField(
        "Has an antiepilepsy medicine been prescribed?",
        default=False
    )
    rescue_medication_prescribed=models.BooleanField(
        "Has a rescue medicine been prescribed?",
        default=False, 
    )
    childrens_epilepsy_surgical_service_referral_criteria_met=models.BooleanField(
        "Have the criteria for referral to a children's epilepsy surgery service been met?",
        default=False
    )
    consultant_paediatrician_referral_made=models.BooleanField(
        "Has a referral been made to a consultant paediatrician with an interest in epilepsy?",
        default=False
    )
    consultant_paediatrician_referral_date=models.DateField(
        "Date of referral to a consultant paediatrician with an interest in epilepsy."
    ) # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    consultant_paediatrician_input_date=models.DateField(
        "Date seen by a consultant paediatrician with an interest in epilepsy."
    ) # National guidance is that children should wait nolonger than x weeks
    paediatric_neurologist_referral_made=models.BooleanField(
        "Has a referral to a consultant paediatric neurologist been made?",
        default=False
    )
    paediatric_neurologist_referral_date=models.DateField(
        "Date of referral to a consultant paediatric neurologist."
    ) # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    paediatric_neurologist_input_date=models.DateField(
        "Date seen by consultant paediatric neurologist."
    ) # National guidance is that children should wait nolonger than x weeks
    childrens_epilepsy_surgical_service_referral_date=models.DateField(
        "Date of referral to a children's epilepsy surgery service",
        blank=True,
        default=None
    )
    childrens_epilepsy_surgical_service_input_date=models.DateField(
        "Date seen by children's epilepsy surgery service",
        blank=True,
        default=None
    )
    were_any_of_the_epileptic_seizures_convulsive=models.BooleanField(
        "Were any of the epileptic seizures convulsive?",
        default=False
    )
    prolonged_generalized_convulsive_seizures=models.CharField(
        "Were there any prolonged generalised epileptic seizures?",
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    experienced_prolonged_focal_seizures=models.CharField(
        "Were there any prolonged focal seizures?",
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    has_an_aed_been_given=models.CharField(
        "Has an antiepilepsy medicine been given?",
        max_length=2, 
        choices=OPT_OUT
    )
    paroxysmal_episode=models.CharField(
        "Were any episodes paroxysmal?",
        max_length=1, 
        choices=OPT_OUT
    )

    # relationships
    antiepilepsy_medicines=models.ManyToManyField(
        AntiEpilepsyMedicine,
        verbose_name="list of antiepilepsy medicines"
    )
    electroclinical_syndrome=models.OneToOneField(
        ElectroClinicalSyndrome,
        on_delete=models.CASCADE,
        verbose_name="related electroclinical syndrome"
    )
    investigations=models.OneToOneField(
        Investigations,
        on_delete=models.CASCADE,
        verbose_name="related investigations"
    )
    registration = models.OneToOneField(
        Registration,
        on_delete=models.DO_NOTHING,
        verbose_name="related registration"
    )
    rescue_medicines=models.ManyToManyField(
        RescueMedicine,
        verbose_name="list of rescue medicines"
    )
    seizure_causes=models.ManyToManyField(
        SeizureCause,
        verbose_name="list of seizure causes"
    )
    nonepilepsy=models.OneToOneField(
        NonEpilepsy,
        on_delete=models.CASCADE,
        verbose_name="related nonepilepsy explanation"
    )

    @property
    def allocate_cohort(self):
        # returns a cohort number 1-3 based on month of year
        if (self.assessment_date.strftime('%m')):
            assessment_month=self.assessment_date.strftime('%m')
            if (assessment_month < 6):
                # between January and May
                return 1
            elif(assessment_month < 9):
                # between Juen and August
                return 2
            else:
                return 3

    class Meta:
        verbose_name="assessment",
        verbose_name_plural="assessments"
    
    def __str__(self) -> str:
        return self.assessment_date


    #TODO #14 Class function to calculate cohort based on first paediatric assessment date
    # this creates a cohort number (integer) based on where in the year they are