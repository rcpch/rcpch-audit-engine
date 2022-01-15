
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
Main classes
The Case class records information about each young person
The Registration class holds a record for each audit.
The Assessment class holds information on each assessment performed over the audit period.
The Episode class holds a record on each seizure and its investigations.
The Site class records information about each site that oversees the epilepsy care of each case.

Other classes
The HospitalTrust class records hospital trust details. It is used as a look up class for the Site class.
The EpilepsyContext class records contextual information that defines epilepsy risk.
The Neurodevelopment class records information about a given neurodevelopmental condition.
The MentalHealth class records information about a given mental health condition.
The AntiEpilepsyDrug class records information about antiepilepsy drugs.
The RescueMedicine class records information on rescue medicines used.
The ElectroclinicalSydrome class records information on electroclinical syndromes.
The NonEpilepsy class records information about nonepilepsy features of episode.
The SeizureType class describes the seizure type.
The SeizureCause class records the cause of each seizure.
The EEG class records information about any EEG performed.


Relationships
-------------
Case to Registration 1:n
Registration to Assessment 1:n
Episode to Assessment 1:n
Case to Episode 1:n

Case to Site 1:n
EpilepsyContext to Case 1:1 (optional)
Case to MentalHealth 1:n
Case to Neurodevelopmental 1:n
Episode to EEG 1:n
Episode to ElectroclinicalSyndrom 1:1
Episode to SeizureCause 1:1
Episode to SeizureType 1:1
Nonepilepsy to Episode 1:1
AntiepilepsyDrug to Episode 1:n
RescueMedicine to Episode 1:n
Case to Neurodevelopment 1:n
Case to MentalHealth 1:n
NonEpilepsy to Episode 1:1
SeizureType to Episode 1:1
SeizureCause to Episode 1:1
Episode to EEG 1:n


HospitalTrust to Site 1:n

"""

from .constants import *
import uuid
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator


# MIXINS

class TimeAndUserStampMixin(models.Model):
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
    locked_at = models.DateTimeField(auto_now_add=True)
    locked_by = models.ForeignKey(
        User, 
        on_delete=CASCADE
    )
    nhs_patient = models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    nhs_chi_number = models.IntegerField( # the Scottish NHS number - is exactly 10 numbers long
        max_length=10, 
        validators=[MinLengthValidator(
            limit_value=10,
            message="The CHI number must be 10 digits long."
        )]
    )
    nhs_number = models.IntegerField( # the NHS number for England and Wales - THIS IS NOT IN THE ORIGINAL TABLES
        max_length=10,
        validators=[MinLengthValidator(
            limit_value=10,
            message="The NHS number must be 10 digits long."
        )]
    )
    first_name=CharField(max_length=100)
    surname=CharField(max_length=100)
    gender=CharField(
        max_length=2,
        choices=SEX_TYPE
    )
    data_of_birth=DateField() #WHY IS THE TIME OF BIRTH NEEDED? I HAVE LEFT THIS OUT
    postcode=CharField(max_length=7)

    class Meta:
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
    site_is_actively_involved_in_care=models.BooleanField(default=False)
    site_is_primary_centre_of_care=models.BooleanField(default=False)
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
class MentalHealth(base.Model):
    """
    This class records information about a given mental health condition
    It references the Case class, as each child might have several mental health conditions
    """
    mental_health_problem=models.CharField(
        max_length=3,
        choices=NEUROPSYCHIATRIC
    )
    mental_health_problem_other=models.CharField(max_length=250)
    mental_health_problem_snomed_code=models.CharField(max_length=50) # this is a new field
    emotional_problem=models.CharField(
        max_length=3, 
        choices=DEVELOPMENTAL_BEHAVIOURAL
    )
    emotional_problem_snomed_code=models.CharField(max_length=50) # this is a new field
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

class Neurodevelopment(base.Model):
    """
    This class records information about a given neurodevelopmental condition
    It references the Case class, as each child might have several neurodevelopmental conditions
    """
    neurodevelopmental_problem=models.CharField(
        max_length=3, 
        choices=NEURODEVELOPMENTAL
    )
    neurodevelopmental_problem_other=models.CharField(max_length=250)
    neurodevelopmental_problem_snomed_code=models.CharField(max_length=50) # this is a new field
    neurodevelopmental_problem_severity=models.CharField(
        max_length=3,
        choices=DISORDER_SEVERITY
    )
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

class Registration(TimeAndUserStampMixin):
    """
    A record is created in the Registration class every time a case is registered for the audit
    A case can be registered only once each audit year, but can be registered in multiple years
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
    diagnostic_status = models.CharField(
        max_length=1,
        choices=DIAGNOSTIC_STATUS
    )
    cohort = IntegerField(validators= [MinValueValidator(1), MaxValueValidator(10)]) # what is this DO WE NEED IT ?

class Assessment(TimeAndUserStampMixin):
    """
    This class stores information on each assessment performed during the registration period.
    This class references the Registration class, as each each assessment belongs to a given audit
    This class is referenced by the Episode class as one assessment can optionally have many episodes
    """
    case=models.ForeignKey(
        Case, 
        on_delete=True)
    epilepsy_years=models.CharField(2, choices=ASSESSMENT)
    opt_out=models.CharField(
        1, 
        choices=OPT_OUT)
    assessment_date=models.DateTimeField()
    has_an_aed_been_given=models.CharField(
        max_length=2, 
        choices=OPT_OUT)
    rescue_medication=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    does_the_child_have_any_of_the_cess_referral_criteria=models.CharField(
        max_length=2, 
        choices=OPT_OUT)
    does_the_child_have_any_of_the_cess_referral_criteria_notes=models.CharField(max_length=250)
    twelve_lead_ecg_status=models.IntegerField(
        2, 
        choices=REFERRAL_STATUS)
    ct_head_scan_status=models.IntegerField(
        2, 
        choices=REFERRAL_STATUS)
    mri_brain_date=models.DateField()
    consultant_paediatrician_involvement_status=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    consultant_paediatrician_input_date=models.DateField()
    paediatric_neurologist_involvement_status=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    paediatric_neurologist_input_date=models.DateField()
    cess=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    cess_input_date=models.DateField()
    registration = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        primary_key=True
    )

class Episode(base.Model):
    """
    This class records information about each seizure episode.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs
    """
    note=CharField(250)
    date_of_referral_to_paediatrics=models.DateField()
    first_paediatric_assessment=models.CharField(
        max_length=2, 
        choices=CHRONICITY
    )
    description_of_the_episode_or_episodes=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    when_the_first_epileptic_episode_occurred_confidence=models.CharField(
        max_length=3, 
        choices=DATE_ACCURACY
    )
    when_the_first_epileptic_episode_occurred=models.DateField()
    frequency_or_number_of_episodes_since_the_first_episode=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    general_examination=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    neurological_examination=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    were_any_of_the_epileptic_seizures_convulsive=models.CharField(
        max_length=2, 
        choices=OPT_OUT
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
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )
    assessment=models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        primary_key=True
    )
    eeg_indicated = BooleanField(default=True)

class EEG(base.Model):
    """
    This class records information about any EEG performed.
    It references the Episode class as each episode may have optionally have several EEGs.
    """
    eeg_date = models.DateTimeField()
    episode = models.ForeignKey(
        Episode,
        on_delete=CASCADE,
        primary_key=True
    )

class ElectroclinicalSyndrome(base.Model):
    """
    This class describes the cause the electroclinical syndrome
    It references the Episode class as each episode optionally forms part of an electroclinical syndrome.
    """
    electroclinical_syndrome=models.IntegerField(choices=ELECTROCLINICAL_SYNDROMES)
    electroclinical_syndrome_other=models.CharField(max_length=250)
    episode = models.OneToOneField(
        Episode,
        on_delete=CASCADE,
        primary_key=True
    )

class SeizureCause(base.Model):
    """
    This class records the cause of each seizure.
    It references the Episode class as each episode optionally has a cause.
    """
    seizure_cause_main=models.CharField(
        max_length=3, 
        choices=EPILEPSY_CAUSES
    )
    seizure_cause_structural=models.CharField(
        max_length=3, 
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES
    )
    seizure_cause_genetic=models.CharField(max_length=3, choices=EPILEPSY_GENETIC_CAUSE_TYPES)
    seizure_cause_chromosomal_abnormality=models.CharField(max_length=200)
    seizure_cause_gene_abnormality=models.CharField(
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
    episode = models.OneToOneField(
        Episode,
        on_delete=CASCADE,
        primary_key=True
    )

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
    developmental_learning_or_schooling_problems=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    behavioural_or_emotional_problems=models.CharField(
        max_length=2, 
        choices=OPT_OUT
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