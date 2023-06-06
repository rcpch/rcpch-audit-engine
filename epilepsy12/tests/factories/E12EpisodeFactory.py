"""Factory fn to create new E12 Episodes, related to a Multiaxial Diagnosis.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Episode,
    Keyword,
)
from epilepsy12.constants import (
    DATE_ACCURACY,
    EPISODE_DEFINITION,
    EPILEPSY_SEIZURE_TYPE,
    GENERALISED_SEIZURE_TYPE,
    NON_EPILEPSY_SEIZURE_ONSET,
    NON_EPILEPSY_SEIZURE_TYPE,
    NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS,
    EPILEPSY_DIAGNOSIS_STATUS,
)

class E12EpisodeFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12MaDFactory.
    
    This E12EpisodeFactory is generated AFTER a E12MaDFactory generated.
    
    Default:
        - Seizure onset 7 days before registration date
        - Approximate date confidence
        - Single Episode
        - Epileptic
        - Description: "the patient was running when they were unresponsive and acalculia"
        - seizure type = Focal Onset
            - Left-sided, atonic with impaired awareness and temporal EEG findings
    
    Flags:
        - `epileptic_seizure_onset_type_generalised`: if True, resets Focal Onset fields, sets Generalised onset with Tonic Clonic
        - `epileptic_seizure_onset_type_unknown`: if True, resets Focal Onset fields, sets to unknown seizure type
        - `epileptic_seizure_onset_type_Unclassified`: if True, resets Focal Onset fields, sets to unclassified seizure type
        - `epilepsy_or_nonepilepsy_status_nonepilepsy`: if True, uses non-epilepsy responses, with first value defined in constants
        - `epilepsy_or_nonepilepsy_status_uncertain`: if True, if True, uses uncertain, no further description
    """
    class Meta:
        model = Episode
    
    # Once MultiaxialDiagnosis instance made, it will attach to this instance
    multiaxial_diagnosis = None
    
    # Once an Episode is made, set seizure_onset_date as 7 days before registration date
    @factory.lazy_attribute
    def seizure_onset_date(self): 
        return self.multiaxial_diagnosis.registration.registration_date - timedelta(days=7)
    
    seizure_onset_date_confidence=DATE_ACCURACY[0][0] # Apx DATE
    
    episode_definition=EPISODE_DEFINITION[0][0] # SINGLE EPISODE
    
    epilepsy_or_nonepilepsy_status = EPILEPSY_DIAGNOSIS_STATUS[0][0] # FIRST EPISODE MUST BE EPILEPTIC, subsequent can be random
    
    has_description_of_the_episode_or_episodes_been_gathered = True 
    
    description = factory.Iterator(Keyword.objects.all(), getter=lambda keywrd: f"Patient was running when they developed {keywrd}")
    description_keywords = factory.Iterator(Keyword.objects.all(), getter=lambda keywrd: [keywrd]) # Episode.description_keywords must be array type
    
    epileptic_seizure_onset_type = EPILEPSY_SEIZURE_TYPE[0][0] # 'FO' Focal onset
    focal_onset_impaired_awareness = True
    focal_onset_automatisms = None
    focal_onset_atonic = True
    focal_onset_clonic = None
    focal_onset_left = True
    focal_onset_right = None
    focal_onset_epileptic_spasms = None
    focal_onset_hyperkinetic = None
    focal_onset_myoclonic = None
    focal_onset_tonic = None
    focal_onset_autonomic = None
    focal_onset_behavioural_arrest = None
    focal_onset_cognitive = None
    focal_onset_emotional = None
    focal_onset_sensory = None
    focal_onset_centrotemporal = None
    focal_onset_temporal = True
    focal_onset_frontal = None
    focal_onset_parietal = None
    focal_onset_occipital = None
    focal_onset_gelastic = None
    focal_onset_focal_to_bilateral_tonic_clonic = None
    
    
    class Params:
        # Helper flag to reset all fields, used by other traits to start with clean fields
        reset = factory.Trait(
                focal_onset_impaired_awareness = None,
                focal_onset_automatisms = None,
                focal_onset_atonic = None,
                focal_onset_clonic = None,
                focal_onset_left = None,
                focal_onset_right = None,
                focal_onset_epileptic_spasms = None,
                focal_onset_hyperkinetic = None,
                focal_onset_myoclonic = None,
                focal_onset_tonic = None,
                focal_onset_autonomic = None,
                focal_onset_behavioural_arrest = None,
                focal_onset_cognitive = None,
                focal_onset_emotional = None,
                focal_onset_sensory = None,
                focal_onset_centrotemporal = None,
                focal_onset_temporal = None,
                focal_onset_frontal = None,
                focal_onset_parietal = None,
                focal_onset_occipital = None,
                focal_onset_gelastic = None,
                focal_onset_focal_to_bilateral_tonic_clonic = None,
        )
        
        # Set appropriate fields if Generalised onset type
        epileptic_seizure_onset_type_generalised = factory.Trait(
            reset=True,
            epileptic_seizure_onset_type = EPILEPSY_SEIZURE_TYPE[1][0], # 'GO' Generalised onset
            epileptic_generalised_onset = GENERALISED_SEIZURE_TYPE[-3][0], # TCl Tonic-clonic
            
        )
        
        # Set appropriate fields if unknown onset type
        epileptic_seizure_onset_type_unknown = factory.Trait(
            reset=True,
            epileptic_seizure_onset_type = EPILEPSY_SEIZURE_TYPE[2][0] # 'UO' "Unknown onset onset
        )
        
        # Set appropriate fields if unclassified onset type
        epileptic_seizure_onset_type_Unclassified = factory.Trait(
            reset=True,
            epileptic_seizure_onset_type = EPILEPSY_SEIZURE_TYPE[3][0] # 'UO' Unclassified onset onset
        )
        
        # Set appropriate fields if episode non-epileptic
        epilepsy_or_nonepilepsy_status_nonepilepsy = factory.Trait(
            reset=True,
            epilepsy_or_nonepilepsy_status = EPILEPSY_DIAGNOSIS_STATUS[1][0],
            nonepileptic_seizure_unknown_onset = NON_EPILEPSY_SEIZURE_ONSET[0][0], # Behavioural arrest
            nonepileptic_seizure_type = NON_EPILEPSY_SEIZURE_TYPE[0][0], # behavioral psychological and psychiatric disorders
            nonepileptic_seizure_behavioural = NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[0][0], # daydreaming / inattention
        )
        # Set appropriate fields if episode uncertain
        epilepsy_or_nonepilepsy_status_uncertain = factory.Trait(
            reset=True,
            epilepsy_or_nonepilepsy_status = EPILEPSY_DIAGNOSIS_STATUS[2][0],
        )