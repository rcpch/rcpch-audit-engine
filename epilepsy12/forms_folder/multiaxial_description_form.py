from django import forms
from django.forms import ModelForm, ChoiceField
from epilepsy12.models.desscribe import DESSCRIBE
from ..constants import *


class MultiaxialDescriptionForm(ModelForm):

    relevant_impairments_behavioural_educational = forms.CheckboxInput(
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MultiaxialDescriptionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DESSCRIBE
        fields = [
            'syndrome',
            'seizure_cause_main',
            'relevant_impairments_behavioural_educational'
        ]
