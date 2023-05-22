"""
Tests the Multiaxial Diagnosis model
More complicated than the others as has 3 related models, each with a one to many relationship
These are:
Episode
Syndrome
Comorbidity

Epilepsy onset fields can be thought of as a group and are stored in constants: 
FOCAL_EPILEPSY_FIELDS, GENERALISED_ONSET_EPILEPSY_FIELDS
NONEPILEPSY_FIELDS

Test cases ensure:
    Episode
    - [ ] at least one MultiaxialDiagnosis.Episode.epilepsy_or_nonepilepsy_status is epileptic ('E')
    - [ ] all MultiaxialDiagnosis.Episode.calculated_score == MultiaxialDiagnosis.Episode.expected_score when all fields completed
    - [ ] a MultiaxialDiagnosis.Episode.description is present if MultiaxialDiagnosis.Episode.has_description_of_the_episode_or_episodes_been_gathered is True
    - [ ] a MultiaxialDiagnosis.Episode.description_keywords are correct for the given description
    - [ ] all nonepilepsy fields including nonepilepsy seizure type fields are None if MultiaxialDiagnosis.Episode.epilepsy_or_nonepilepsy_status == 'E' (epilepsy)
    - [ ] all epilepsy fields are None if MultiaxialDiagnosis.Episode.epilepsy_or_nonepilepsy_status == 'E' (epilepsy) or U (Unknown)
    - [ ] all generalised onset epilepsy fields are None if MultiaxialDiagnosis.Episode.epileptic_seizure_onset_type == 'FO' (focal onset)
    - [ ] all focal onset epilepsy fields are None if MultiaxialDiagnosis.Episode.epileptic_seizure_onset_type == 'GO' (generalised onset)
    - [ ] all focal and generalised onset epilepsy fields are None if MultiaxialDiagnosis.Episode.epileptic_seizure_onset_type == 'UO' or 'UC' (unknow onset or unclassified)
        Nonepilepsy seizure types - choices are NON_EPILEPSY_SEIZURE_TYPE
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_behavioural 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'BPP' (Behavioural, Psychological and Psychiatric)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_migraine 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'MAD' (Migraine Associated Disorders)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_miscellaneous  
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'ME' (Miscellaneous Events)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_sleep 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'SRC' (Sleep Related Conditions)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_syncope 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'SAS' (Syncope and Anoxic Seizures)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_paroxysmal 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'PMD' (Paroxysmal Movement Disorders)
    - [ ] all nonepilepsy seizure fields are None except MultiaxialDiagnosis.Episode.nonepileptic_seizure_unknown_onset 
    if MultiaxialDiagnosis.Episode.nonepileptic_seizure_type == 'Oth' (Other)
    Syndromes
    - [ ] there is at least one MultiaxialDiagnosis.syndrome.pk if MultiaxialDiagnosis.syndrome_present is True
    - [ ] each instance of MultiaxialDiagnosis.syndrome has valid syndrome_diagnosis_date
    - [ ] each instance of MultiaxialDiagnosis.syndrome has valid syndrome
    - [ ] each instance of MultiaxialDiagnosis.syndrome has both syndrome_diagnosis_date and syndrome completed
    Epilepsy Causes
    - [ ] there is one instance of MultiaxialDiagnosis.epilepsy_cause if MultiaxialDiagnosis.epilepsy_cause_known is True
    - [ ] there is at least one item in the array of MultiaxialDiagnosis.epilepsy_cause_categories if MultiaxialDiagnosis.epilepsy_cause_known is True
    Comorbidities
    - [ ] there is one instance of MultiaxialDiagnosis.comorbidity if MultiaxialDiagnosis.relevant_impairments_behavioural_educational is True
    - [ ] for every instance of MultiaxialDiagnosis.comorbidity there is a MultiaxialDiagnosis.comorbidity.comorbidity_diagnosis_date
    - [ ] for every instance of MultiaxialDiagnosis.comorbidity there is an instance of MultiaxialDiagnosis.comorbidity.comorbidity_entity
    Multiaxial diagnosis
    - [ ] MultiaxialDiagnosis.global_developmental_delay_or_learning_difficulties_severity is not None if MultiaxialDiagnosis.global_developmental_delay_or_learning_difficulties is True
    - [ ] MultiaxialDiagnosis.mental_health_issue_identified is not None if MultiaxialDiagnosis.mental_health_screen is True



    
    






"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    MultiaxialDiagnosis,
    Episode,
)


@pytest.mark.django_db
def test_working_e12MultiaxialDiagnosis_e12Case_relation(e12MultiaxialDiagnosis_2022):
    multiaxial_diagnosis = e12MultiaxialDiagnosis_2022
    print(multiaxial_diagnosis.registration)

    episode = Episode.objects.get(multiaxial_diagnosis=multiaxial_diagnosis)

    for field, value in episode.__dict__.items():
        print(f"{field}: {value}")
