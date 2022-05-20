from django import forms
from django.forms import ModelForm, ChoiceField
from epilepsy12.models.desscribe import DESSCRIBE
from ..constants import *


class MultiaxialDescriptionForm(ModelForm):

    relevant_impairments_behavioural_educational = forms.CheckboxInput(
    )
    epileptic_seizure_type = ChoiceField(
        help_text="If epileptic, what is the seizure type (s)?",
        choices=EPILEPSY_SEIZURE_TYPE,
    )
    non_epileptic_seizure_type = ChoiceField(
        help_text="If epileptic, what is the seizure type (s)?",
        choices=NON_EPILEPSY_SEIZURE_TYPE,
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MultiaxialDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['description_keywords'].widget.attrs = {
            'type': 'text',
            'placeholder': 'Description',
            'class': 'prompt'
        }

    class Meta:
        model = DESSCRIBE
        fields = [
            'description',
            'description_keywords',
            'epilepsy_or_nonepilepsy_status',
            'epileptic_seizure_type',
            'non_epileptic_seizure_type',
            'focal_onset_impaired_awareness',
            'focal_onset_automatisms',
            'focal_onset_atonic',
            'focal_onset_clonic',
            'focal_onset_left',
            'focal_onset_right',
            'focal_onset_epileptic_spasms',
            'focal_onset_hyperkinetic',
            'focal_onset_myoclonic',
            'focal_onset_tonic',
            'focal_onset_autonomic',
            'focal_onset_behavioural_arrest',
            'focal_onset_cognitive',
            'focal_onset_emotional',
            'focal_onset_sensory',
            'focal_onset_centrotemporal',
            'focal_onset_temporal',
            'focal_onset_frontal',
            'focal_onset_parietal',
            'focal_onset_occipital',
            'focal_onset_gelastic',
            'focal_onset_focal_to_bilateral_tonic_clonic',
            'focal_onset_other',
            'focal_onset_other_details',
            'generalised_onset',
            'generalised_onset_other_details',
            'nonepileptic_seizure_unknown_onset',
            'nonepileptic_seizure_unknown_onset_other_details',
            'nonepileptic_seizure_syncope',
            'nonepileptic_seizure_behavioural',
            'nonepileptic_seizure_sleep',
            'nonepileptic_seizure_paroxysmal',
            'nonepileptic_seizure_migraine',
            'nonepileptic_seizure_miscellaneous',
            'nonepileptic_seizure_other',
            'syndrome',
            'seizure_cause_main',
            'relevant_impairments_behavioural_educational'
        ]
