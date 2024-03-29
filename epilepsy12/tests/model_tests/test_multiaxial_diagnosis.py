"""

TODO MOVE TO DIFFERENT TEST FILE:
    - [ ] all MultiaxialDiagnosis.Episode.calculated_score == MultiaxialDiagnosis.Episode.expected_score when all fields completed
    
    
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
    - [x] at least one MultiaxialDiagnosis.Episode.epilepsy_or_nonepilepsy_status is epileptic ('E')
    - [x] a MultiaxialDiagnosis.Episode.description is present if MultiaxialDiagnosis.Episode.has_description_of_the_episode_or_episodes_been_gathered is True
    - [x] a MultiaxialDiagnosis.Episode.description_keywords are correct for the given description
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
from django.core.exceptions import ValidationError

# RCPCH imports
from epilepsy12.models import (
    Episode,
    Syndrome,
    Comorbidity,
    Keyword,
)
from epilepsy12.constants import (
    EPILEPSY_DIAGNOSIS_STATUS,
)


@pytest.mark.xfail
@pytest.mark.django_db
def test_at_least_one_MultiaxialDiagnosis__Episode_is_epileptic(
    e12_case_factory,
):

    # creates multiaxial diagnosis where only episode is non epileptic. Assert validation error on save (called automatically when creating subFactories)
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__multiaxial_diagnosis__episode__epilepsy_or_nonepilepsy_status=EPILEPSY_DIAGNOSIS_STATUS[
                1
            ][
                0
            ]
        )

@pytest.mark.xfail
@pytest.mark.django_db
def test_Episode_validation_description_must_be_present_when_DescriptionOfEpisode_True(
    e12_case_factory,
):
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__multiaxial_diagnosis__episode__has_description_of_the_episode_or_episodes_been_gathered=True,
            registration__multiaxial_diagnosis__episode__description=None,
        )

@pytest.mark.xfail
@pytest.mark.django_db
def test_Episode_validation_description_keywords_correct_for_description(
    e12_case_factory,
):
    KEYWORDS = Keyword.objects.all()
    description = (
        f"Patient was running when they {KEYWORDS[0]}, {KEYWORDS[1]}, and {KEYWORDS[2]}"
    )

    # create an Episode with the wrong keywords stored, try to save, should raise validation error
    # ALL WRONG
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__multiaxial_diagnosis__episode__description=description,
            registration__multiaxial_diagnosis__episode__description_keywords=[
                KEYWORDS[3],
                KEYWORDS[4],
                KEYWORDS[5],
            ],
        )
    # 1 WRONG
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__multiaxial_diagnosis__episode__description=description,
            registration__multiaxial_diagnosis__episode__description_keywords=[
                KEYWORDS[0],
                KEYWORDS[1],
                KEYWORDS[5],
            ],
        )
