from django import forms
from django.forms import ModelForm
from django.urls import reverse_lazy
from epilepsy12.models import DESSCRIBE
from epilepsy12.models.desscribe import DESSCRIBE
from ..constants import *

"""
Holds all the form classes for the DESSCRIBE model
Each form is broken into different dependent fields to allow HTMX rendering
"""


class MultiaxialDescriptionForm(ModelForm):

    focal_onset_atonic = forms.CheckboxInput()
    relevant_impairments_behavioural_educational = forms.CheckboxInput()

    def __init__(self, *args, **kwargs) -> None:
        super(MultiaxialDescriptionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DESSCRIBE
        fields = (
            'epilepsy_or_nonepilepsy_status',
            'syndrome',
            'seizure_cause_main',
            'relevant_impairments_behavioural_educational'
        )


class DescriptionForm(ModelForm):

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'name': 'description', 'rows': '3',
                   'placeholder': 'While watching television...'}
        )
    )

    def __init__(self, *args, **kwargs) -> None:
        super(DescriptionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DESSCRIBE
        fields = ('description', 'description_keywords')
