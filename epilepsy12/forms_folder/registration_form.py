
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
                "class": "form-control",
                "placeholder": "registration date",
                "type": "date"
            }
        )
    )
    referring_clinician = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Referring Clinician"
            }
        )
    )

    registration_close_date = forms.DateField(
        required=False
    )

    cohort = forms.IntegerField(
        required=False
    )

    # lead_hospital = forms.CharField(
    #     widget=autocomplete.ModelSelect2(
    #         url=reverse_lazy('hospital-autocomplete'),
    #         attrs={
    #             'data-placeholder': 'Autocomplete ...',
    #             # Only trigger autocompletion after 3 characters have been typed
    #             'data-minimum-input-length': 3,
    #         },
    #     )
    # )

    # tertiary_paediatric_neurology_centre = forms.CharField(
    #     widget=autocomplete.ModelSelect2(
    #         url='hospital-autocomplete'),
    #         attrs={
    #             'data-placeholder': 'Autocomplete ...',
    #             # Only trigger autocompletion after 3 characters have been typed
    #             'data-minimum-input-length': 3,
    #         },
    #     )
    # )

    # epilepsy_surgery_centre=forms.CharField(
    #     widget = autocomplete.ModelSelect2(
    #         url='hospital-autocomplete',
    #         attrs={
    #             'data-placeholder': 'Autocomplete ...',
    #             # Only trigger autocompletion after 3 characters have been typed
    #             'data-minimum-input-length': 3,
    #         },
    #     )
    # )

    # def __init__(self, *args, **kwargs) -> None:
    #     super(RegistrationForm, self).__init__(*args, **kwargs)

    class Meta():
        model = Registration
        fields = (
            'registration_date',
            'referring_clinician',
            'registration_close_date'
        )
        # widgets = {
        #     'lead_hospital': autocomplete.ModelSelect2(url='hospital-autocomplete'),
        #     'tertiary_paediatric_neurology_centre': autocomplete.ModelSelect2(url='hospital-autocomplete'),
        #     'epilepsy_surgery_centre': autocomplete.ModelSelect2(url='hospital-autocomplete'),
        # }
