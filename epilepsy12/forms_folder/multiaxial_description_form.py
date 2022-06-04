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

    relevant_impairments_behavioural_educational = forms.CheckboxInput(
    )

    focal_onset_atonic = forms.CheckboxInput()
    focal_onset_clonic = forms.CheckboxInput()

    def __init__(self, *args, **kwargs) -> None:
        super(MultiaxialDescriptionForm, self).__init__(*args, **kwargs)
        url = reverse_lazy('seizure_cause_main')

        self.fields['syndrome'].widget.attrs['class'] = "ui dropdown"
        self.fields['seizure_cause_main'].widget.attrs['hx-post'] = reverse_lazy(
            'seizure_cause_main')

    class Meta:
        model = DESSCRIBE
        fields = (
            'focal_onset_atonic',
            'focal_onset_clonic',
            'focal_onset_occipital',
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
