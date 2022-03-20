from email.policy import default
from django import forms

from epilepsy12.models.epilepsy_context import EpilepsyContext
from epilepsy12.models.comorbidity import Comorbidity

from ..constants import *


class EpilepsyContextForm(forms.ModelForm):

    previous_febrile_seizure = forms.ChoiceField(
        help_text="has there been a previous febrile seizure?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_acute_symptomatic_seizure = forms.ChoiceField(
        help_text="has there been a previous acute symptomatic seizure?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    is_there_a_family_history_of_epilepsy = forms.ChoiceField(
        help_text="is there a family history of epilepsy?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_neonatal_seizures = forms.ChoiceField(
        help_text="were there seizures in the neonatal period?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    diagnosis_of_epilepsy_withdrawn = forms.ChoiceField(
        help_text="has the diagnosis of epilepsy been withdrawn?",
        choices=OPT_OUT,
        initial=OPT_OUT[1][0]
    )
    date_of_first_epileptic_seizure = forms.DateField(
        help_text="What date was the first reported epileptic seizure?",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of first seizure",
                "type": "date"
            }
        )
    )
    epilepsy_decimal_years = forms.FloatField(
        help_text="Number of years since first seizure.",
        required=False
    )

    class Meta:
        model = EpilepsyContext
        fields = [
            'previous_febrile_seizure',
            'previous_acute_symptomatic_seizure',
            'is_there_a_family_history_of_epilepsy',
            'previous_neonatal_seizures',
            'diagnosis_of_epilepsy_withdrawn',
            'date_of_first_epileptic_seizure',
            'epilepsy_decimal_years'
        ]
