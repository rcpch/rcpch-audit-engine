from operator import mod
from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class SeizureType(TimeAndUserStampMixin):
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

    # relationships
    assessment=models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        primary_key=True
    )

    #TODO this class needs to be referenced by Case