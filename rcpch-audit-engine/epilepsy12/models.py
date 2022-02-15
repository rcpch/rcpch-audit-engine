
from django.db import models
from django.db.models import base, indexes
from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField, CharField, DateField, DateTimeField, IntegerField
from .constants import *

"""
Stated Aims of the Audit
• Continue to measure and improve care and outcomes for children and young people with
epilepsies
• Include all children and young people with a new onset of epilepsy,
• Enable continuous patient ascertainment,
• Use a pragmatic and concise dataset,
• Incorporate NICE Quality Standards alongside metrics about mental health, education and
transition to adult services,
• Provide services with local real-time patient- and service-level reporting.

Quality Improvement
- Supporting regional and national quality improvement activities
- Epilepsy Quality Improvement Programme (EQIP)
- Involving children and young people

There are 12 key performance indicators:
1. Input into care from a paediatrician with expertise in epilepsies,
2. Input into care from an epilepsy specialist nurse (ESNs),
3. (a) Appropriate tertiary input into care, and (b) appropriate epilepsy surgery referral
4. Appropriate first paediatric assessment,
5. Recorded seizure formulation,
6. Access to electrocardiogram (ECG),
7. Access to magnetic resonance imaging (MRI),
8. Accuracy of diagnosis,
9. (a) Discussion of the risks where sodium valproate is used in treatment for girls aged 9 and over,
and (b) girls and young women prescribed sodium valproate
10. Comprehensive care plan that is updated and agreed with the patient,
11. Documented evidence of all key elements of care planning content,
12. Record of a school individual healthcare plan.

Schema
------
*Main classes*
The Case class records information about each young person
The Registration class holds a record for each audit.
The Assessment class holds information on cases gathered over the one year audit period.
The InitialAssessment class is closely linked to Assessment and holds the minimum expected information collected at first assessment.  
The Investigations class records dates that initial tests were recorded (ECG, EEG, CT and MRI)
The EpilepsyContext class records contextual information that defines epilepsy risk.
The Comorbidity class records information on emotional, behavioural, neurodevelopmental and neuropsychatric comorbidities

The RescueMedicine class records information on rescue medicines used.
The AntiEpilepsyDrug class records information about antiepilepsy drugs.


The SeizureType class describes the seizure type.
The ElectroclinicalSydrome class records information on electroclinical syndromes.
The SeizureCause class records the cause of each seizure.
The NonEpilepsy class records information about nonepilepsy features of episode.

The Site class records information about each site that oversees the epilepsy care of each case.
The HospitalTrust class records hospital trust details. It is used as a look up class for the Site class.


Relationships
-------------
Case to Registration 1:1
Case to Site 1:n
Registration to Assessment 1:1
InitialAssessment to Assessment 1:1
EpilepsyContext to Case 1:1
Comorbidity to Case n:n
Assessment to Investigations 1:1
RescueMedicine to Assessment 1:1
Case to Comorbidity 1:n

RescueMedicine to Assessment 1:n

Case to Site 1:n

Assessment to ElectroclinicalSyndrome 1:1
Assessment to SeizureCause 1:1
Assessment to SeizureType 1:1


NonEpilepsy to Assessment 1:1
SeizureType to Assessment n:1
SeizureCause to Assessment n:1


HospitalTrust to Site 1:n

"""

from .constants import *
import uuid
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator


# MIXINS

class TimeAndUserStampMixin(models.Model): #TODO #12 Mixin breaks build currently
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=CASCADE)

    class Meta:
        abstract = True

# TABLES

class HospitalTrust(base.Model):
    """
    This class details information about hospital trusts.
    It represents a list of hospital trusts that can be looked up to populate fields in the Site class
    """
    hospital_trust_name=models.CharField(
        max_length=100,
        verbose_name="hospital trust full name"
    )
    # ... any other details about the hospital we need
    class Meta:
        indexes=[models.Index(fields=['hospital_trust_name'])]
        ordering = ['-hospital_trust_name']
        verbose_name = 'hospital trust'
        verbose_name_plural = 'hospital trusts'

    def __str__(self) -> str:
        return self.hospital_trust_name
class Case(TimeAndUserStampMixin):
    """
    This class holds information about each child or young person
    Each case is unique
    This class holds patient characteristics including identifiers
    This class is referenced by the Site class, as each case can be seen in multiple sites
    This class is referenced by the Neurodevelopmental class as each case can have multiple neurodevelopmental conditions
    This class is referenced by the MentalHealth class as each case can have multiple mental health conditions
    This class is referenced by the EpilepsyContext class as each case may optionally have contextual information that may inform the epilepsy history

    For a record to be locked:
    1. all mandatory fields must be complete
    2. NHS number must be present
    3. 1 year must have passed

    ?analysis flag
    """
    case_uuid=models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    locked=models.BooleanField( # this determines if the case is locked from editing ? are cases or only registrations locked?
        "Locked", 
        default=False
    )
    locked_at = models.DateTimeField(
        auto_now_add=True
    )
    locked_by = models.ForeignKey(
        User, 
        on_delete=CASCADE,
        related_name='case_locked'
    )
    nhs_patient = models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    nhs_number = models.IntegerField( # the NHS number for England and Wales - THIS IS NOT IN THE ORIGINAL TABLES
        max_length=10,
        validators=[MinLengthValidator( # should be other validation before saving - need to strip out spaces
            limit_value=10,
            message="The NHS number must be 10 digits long."
        )]
    ) # TODO #13 NHS Number must be hidden - use case_uuid as proxy
    first_name=CharField(
        max_length=100
    )
    surname=CharField(
        max_length=100
    )
    gender=CharField(
        max_length=2,
        choices=SEX_TYPE
    )
    date_of_birth=DateField()
    postcode=CharField( # TODO #6 need to validate postcode
        max_length=7
    )
    index_of_multiple_deprivation=CharField( # TODO #5 need to calculate IMD and persist
        
    )
    index_of_multiple_deprivation_quintile=CharField( # TODO #4 need to calculate IMD quintile and persist

    )
    
    ethnicity=CharField(
        # TODO #7 There needs to be a standard look up for ethnicities - DM&D
        max_length=4,
        choices=ETHNICITIES
    )

    class Meta: #TODO #16 add meta classes to all classes
        indexes=[models.Index(fields=['case_uuid'])]
        ordering = ['-surname']
        verbose_name = 'child or young person'
        verbose_name_plural = 'children and young people'

    def __str__(self) -> str:
        return self.hospital_trust_name

class Site(TimeAndUserStampMixin):
    """
    This class records information about each site that oversees the epilepsy care of each case.
    This class references the HospitalTrust class, as one hospital trust may reference multiple sites
    This class references the Case class, as each case may have multiple sites.
    """
    hospital_trust=models.ForeignKey(
        HospitalTrust, 
        on_delete=models.CASCADE,
        related_name='hospital trusts',
        related_query_name='hospitals'
    )
    site_is_actively_involved_in_epilepsy_care=models.BooleanField(default=False)
    site_is_primary_centre_of_epilepsy_care=models.BooleanField(
        default=False,
        unique=True
    )
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

    class Meta:
        ordering = ['-hospital_trust']
        verbose_name = 'site'
        verbose_name_plural = 'sites'

    def __str__(self) -> str:
        return self.hospital_trust

class Comorbidity(base.Model):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    [This class replaces the MentalHealth and Neurodevelopmental tables, conflating options into one list]
    It references the Case class as each child may have several comorbidities

    Detail
    The date of onset/diagnosis field has been actively removed as not found helpful
    """
    comorbidity=models.CharField(
        max_length=3,
        choices=COMORBIDITIES
    )
    comorbidity_free_text=models.CharField( # this is a free text field for 'other' diagnoses not included in the lists provided
        max_length=50,
        default=None
    )
    comorbidity_snomed_code=models.CharField( #TODO #11 Need to tag Snomed CT terms to all comorbidites @marcusbaw @colindunkley
        max_length=50
    ) # this is a new field - decision not to act on this currently: rare for a formal diagnosis to be give so
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

class Registration(TimeAndUserStampMixin):
    """
    A record is created in the Registration class every time a case is registered for the audit
    A case can be registered only once - TODO Merge Registration with Case class
    """
    registration_uuid=models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    case=models.models.ForeignKey(
        Case, 
        on_delete=CASCADE,
        primary_key=True)
    site=models.ForeignKey(
        Site, 
        on_delete=CASCADE,
        primary_key=True)
    locked=models.BooleanField( # this determines if the case is locked from editing ? are cases or only registrations locked?
        "Locked", 
        default=False
    )
    locked_at = models.DateTimeField(auto_now_add=True)
    locked_by = models.ForeignKey(
        User, 
        on_delete=CASCADE
    )
    closed=models.BooleanField( # this determines if the case is closed? ARE CASES CLOSED AS WELL AS LOCKED OR REGISTRATIONS?
        "Closed", 
        default=False
    )
    referring_hospital = models.ForeignKey(
        HospitalTrust, 
        on_delete=CASCADE
    )
    referring_clinician = models.CharField(max_length=50)
    diagnostic_status = models.CharField( # This currently essential - used to exclude nonepilepic kids
        max_length=1,
        choices=DIAGNOSTIC_STATUS
    )

class Assessment(TimeAndUserStampMixin):
    """
    This class stores information on each assessment performed during the registration period.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """
    case=models.OneToOneField(
        Case, 
        on_delete=False)
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

    #TODO #14 Class function to calculate cohort based on first paediatric assessment date
    # this creates a cohort number (integer) based on where in the year they are

    # TODO #15 Class function to create calculated field epilepsy_years based on current date and date of first seizure in years

class InitialAssessment(base.Model):
    """
    This class records information about each seizure episode.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    On Episode
    """
    
    date_of_referral_to_general_paediatrics=models.DateField()
    first_paediatric_assessment_in_acute_or_nonacute_setting=models.CharField(
        max_length=2, 
        choices=CHRONICITY
    )
    has_description_of_the_episode_or_episodes_been_gathered=models.BooleanField(
        default=False
    )
    when_the_first_epileptic_episode_occurred_confidence=models.CharField(
        max_length=3, 
        choices=DATE_ACCURACY
    )
    when_the_first_epileptic_episode_occurred=models.DateField()
    has_frequency_or_number_of_episodes_since_the_first_episode_been_documented=models.BooleanField(
        default=False
    )
    general_examination_performed=models.BooleanField(
        default=False
    )
    neurological_examination_performed=models.BooleanField(
        default=False
    )
    developmental_learning_or_schooling_problems=models.BooleanField(
        default=False
    )
    behavioural_or_emotional_problems=models.BooleanField(
        default=False
    )
    case = models.OneToOneField(
        Case,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    assessment=models.OneToOneField(
        Assessment,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )

class Investigations(base.Model):
    """
    This class records information about any EEG performed.
    It references the Assessment class as each episode may have optionally have several EEGs.
    """
    eeg_indicated = BooleanField(default=True)
    eeg_request_date = models.DateTimeField()
    eeg_performed_date = models.DateTimeField()
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    twelve_lead_ecg_status=models.BooleanField(
        default=False
    )
    ct_head_scan_status=models.BooleanField(
        default=False
    )
    mri_brain_date=models.DateField()
    consultant_paediatrician_referral_made=models.BooleanField(
        default=False
    )

class ElectroclinicalSyndrome(base.Model):
    """
    This class describes the cause the electroclinical syndrome
    It references the Episode class as each episode optionally forms part of an electroclinical syndrome.

    Is this class really needed??
    One Case can have multiple Electroclinical Syndrome
    """
    electroclinical_syndrome=models.IntegerField(choices=ELECTROCLINICAL_SYNDROMES)
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

    #TODO this class needs to be referenced by Case

class SeizureCause(base.Model):
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
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

    #TODO this class needs to be referenced by Case

class SeizureType(base.Model):
    """
    This class records the seizure type.
    COULD IT BE ORGANISED DIFFERENTLY - IT SEEMS TO BE A LOT OF BOOLEANS
    This class references the Episode class as each episode optionally has a single episode type
    """
    epilepsy_or_nonepilepsy_status=models.CharField(
        max_length=3,
        choices=EPILEPSY_DIAGNOSIS_STATUS
    )
    epileptic_seizure_type=models.CharField(
        max_length=3,
        choices=EPILEPSY_SEIZURE_TYPE
    )
    non_epileptic_seizure_type=models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_TYPE
    )
    focal_onset_impaired_awareness=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_automatisms=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_atonic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_clonic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_left=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_right=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_epileptic_spasms=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_hyperkinetic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_myoclonic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_tonic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_autonomic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_behavioural_arrest=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_cognitive=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_emotional=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_sensory=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_centrotemporal=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_temporal=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_frontal=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_parietal=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_occipital=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_gelastic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_focal_to_bilateral_tonic_clonic=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_other=models.IntegerField(choices=CHECKED_STATUS)
    focal_onset_other_details=models.CharField(max_length=250)
    generalised_onset=models.CharField(
        max_length=3, 
        choices=GENERALISED_SEIZURE_TYPE)
    generalised_onset_other_details=models.CharField(max_length=250)
    nonepileptic_seizure_unknown_onset=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_SEIZURE_ONSET)
    nonepileptic_seizure_unknown_onset_other_details=models.CharField(max_length=250)
    nonepileptic_seizure_syncope=models.CharField(
        max_length=3,
        choices=NON_EPILEPTIC_SYNCOPES)
    nonepileptic_seizure_behavioural=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    nonepileptic_seizure_sleep=models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    nonepileptic_seizure_paroxysmal=models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_PAROXYSMS)
    nonepileptic_seizure_migraine=models.CharField(
        max_length=3,
        choices=MIGRAINES)
    nonepileptic_seizure_miscellaneous=models.CharField(
        max_length=3,
        choices=EPIS_MISC)
    nonepileptic_seizure_other=models.CharField(max_length=250)
    episode = models.OneToOneField(
        Episode,
        on_delete=CASCADE,
        primary_key=True
    )

    #TODO this class needs to be referenced by Case

class EpilepsyContext(base.Model):
    """
    This class records contextual information that defines epilepsy risk.
    It references the Case class, as each case optionally has a single epilepsy context.
    """
    previous_febrile_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    previous_acute_symptomatic_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    is_there_a_family_history_of_epilepsy=models.CharField(
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    previous_neonatal_seizures=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    diagnosis_of_epilepsy_withdrawn=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    case = models.OneToOneField(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )
class NonEpilepsy(base.Model):
    """
    This class records information about nonepilepsy features of episode.
    This class optionally references the Episode class as one episode can have one set of nonepilepsy features.
    """
    nonepilepsy_type=models.IntegerField(choices=EPIS_TYPE)
    nonepilepsy_syncope=models.CharField(
        max_length=3, 
        choices=NON_EPILEPTIC_SYNCOPES)
    nonepilepsy_behavioural=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    nonepilepsy_sleep=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    nonepilepsy_paroxysmal=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_PAROXYSMS)
    nonepilepsy_migraine=models.CharField(
        max_length=3,
        choices=MIGRAINES)
    nonepilepsy_miscellaneous=models.CharField(
        max_length=3, 
        choices=EPIS_MISC)
    nonepilepsy_other=models.CharField(max_length=250)
    episode = models.OneToOneField(
        Episode,
        on_delete=models.CASCADE,
        primary_key=True
    )

class AntiEpilepticDrug(base.Model):
    """
    This class records information about antiepilepsy drugs. 
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """
    anti_epileptic_drug_type=models.IntegerField(choices=ANTI_EPILEPTIC_DRUG_TYPES)
    anti_epileptic_drug_type_other=models.CharField(50)
    anti_epileptic_drug_snomed_code=models.CharField(50) # this is a new field
    anti_epileptic_start_date=models.models.DateField()
    anti_epileptic_stop_date=models.models.DateField()
    anti_epilepsy_drug_risk_discussed=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    ) # is this what you mean by risk? that it has been discussed?
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        primary_key=True
    )

class RescueMedicine(base.Model):
    """
    This class records information on rescue medicines used.
    It references the Episode class, since one episode can involve the use of several medicines
    """
    rescue_medicine_type=models.CharField(
        max_length=3,
        choices=BENZODIAZEPINE_TYPES
    )
    rescue_medicine_other=models.CharField(max_length=100)
    rescue_medicine_start_date=models.DateField()
    rescue_medicine_stop_date=models.DateField()
    rescue_medicine_status=models.IntegerField(choices=CHECKED_STATUS)
    rescue_medicine_notes=models.CharField(max_length=250)
    episode=models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        primary_key=True
    )

class ElectroClinicalSyndrome(base.Model):
    """
    This class records information on electroclinical syndromes.
    It references the episode class, since one episode can have features of a single electroclinical syndrome.
    """
    electroclinical_syndrome=models.IntegerField(choices=ELECTROCLINICAL_SYNDROMES)
    electroclinical_sydrome_other=models.CharField(max_length=250)
    episode = models.OneToOneField(
        Episode,
        on_delete=models.CASCADE,
        primary_key=True
    )



"""
COMMENTING OUT THESE TABLES AND REPLACING WITH COMORBIDITIES
"""

# class MentalHealth(base.Model): 
#     """
#     This class records information about a given mental health condition
#     It references the Case class, as each child might have several mental health conditions
#     """
#     mental_health_problem=models.CharField( # TODO #8 Decision to leave mental health problems the same: will need to be SNOMED in future
#         max_length=3,
#         choices=NEUROPSYCHIATRIC
#     )
#     mental_health_problem_snomed_code=models.CharField(
#         max_length=50
#     ) # this is a new field - decision not to act on this currently: rare for a formal diagnosis to be give so
#     # not practical
#     emotional_problem=models.CharField(
#         max_length=3, 
#         choices=DEVELOPMENTAL_BEHAVIOURAL
#     )
#     emotional_problem_snomed_code=models.CharField(max_length=50) # this is a new field
#     case = models.ForeignKey(
#         Case,
#         on_delete=CASCADE,
#         primary_key=True
#     )

# class Neurodevelopment(base.Model):
#     """
#     This class records information about a given neurodevelopmental condition
#     It references the Case class, as each child might have several neurodevelopmental conditions
#     """
#     neurodevelopmental_problem=models.CharField(
#         max_length=3, 
#         choices=NEURODEVELOPMENTAL
#     )
#     neurodevelopmental_problem_other=models.CharField(max_length=250)
#     neurodevelopmental_problem_snomed_code=models.CharField(max_length=50) # this is a new field
#     neurodevelopmental_problem_severity=models.CharField(
#         max_length=3,
#         choices=DISORDER_SEVERITY
#     )
#     case = models.ForeignKey(
#         Case,
#         on_delete=CASCADE,
#         primary_key=True
#     )