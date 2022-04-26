
from ast import arg
from django import forms
from django.urls import reverse_lazy
from ..models import Registration
from ..constants import *

# third party imports
from dal import autocomplete


class RegistrationForm(forms.ModelForm):
    registration_date = forms.DateField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'registration date',
                'type': 'date'
            }
        )
    )
    referring_clinician = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Referring Clinician'
            }
        )
    )

    registration_close_date = forms.DateField(
        required=False
    )

    cohort = forms.IntegerField(
        required=False
    )

    def __init__(self, *args, **kwargs) -> None:
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['epilepsy_surgery_centre'].widget.attrs = {
            'type': 'text',
            'placeholder': 'Epilepsy Surgery Centre',
            'class': 'prompt'
        }
        self.fields['lead_hospital'].widget.attrs = {
            'type': 'text',
            'placeholder': 'Lead Centre',
            'class': 'prompt'
        }
        self.fields['tertiary_paediatric_neurology_centre'].widget.attrs = {
            'type': 'text',
            'placeholder': 'Tertiary Paediatric Neurology Centre',
            'class': 'prompt'
        }

    class Meta():
        model = Registration
        fields = (
            'registration_date',
            'referring_clinician',
            'registration_close_date',
            'lead_hospital',
            'tertiary_paediatric_neurology_centre',
            'epilepsy_surgery_centre'
        )
