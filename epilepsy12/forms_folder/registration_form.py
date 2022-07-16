
from ast import arg
from django import forms
from django.urls import reverse_lazy
from ..models import Registration
from ..constants import *


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

    class Meta():
        model = Registration
        fields = (
            'registration_date',
            'referring_clinician',
            'registration_close_date',
            'cohort'
        )
