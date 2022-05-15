from django import forms
from django.forms import ModelForm, ChoiceField
from epilepsy12.models.desscribe import DESSCRIBE
from ..constants import *


class MultiaxialDescriptionForm(ModelForm):

    relevant_impairments_behavioural_educational = forms.CheckboxInput(
    )
    seizure_type = ChoiceField(
        help_text="If epileptic, what is the seizure type (s)?",
        choices=EPILEPSY_SEIZURE_TYPE,
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
            'epilepsy_status',
            'seizure_type',
            'syndrome',
            'cause',
            'relevant_impairments_behavioural_educational'
        ]
