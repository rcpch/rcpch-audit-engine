from email.policy import default
from django.forms import BaseInlineFormSet, CharField, ModelForm, ChoiceField, DateField, TextInput

from epilepsy12.models.epilepsy_context import EpilepsyContext

from ..constants import *


class EpilepsyContextForm(ModelForm):

    previous_febrile_seizure = ChoiceField(
        help_text="has there been a previous febrile seizure?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_acute_symptomatic_seizure = ChoiceField(
        help_text="has there been a previous acute symptomatic seizure?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    is_there_a_family_history_of_epilepsy = ChoiceField(
        help_text="is there a family history of epilepsy?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_neonatal_seizures = ChoiceField(
        help_text="were there seizures in the neonatal period?",
        choices=OPT_OUT_UNCERTAIN,
        initial=OPT_OUT_UNCERTAIN[1][0]
    )
    diagnosis_of_epilepsy_withdrawn = ChoiceField(
        help_text="has the diagnosis of epilepsy been withdrawn?",
        choices=OPT_OUT,
        initial=OPT_OUT[1][0]
    )
    date_of_first_epileptic_seizure = DateField(
        help_text="What date was the first reported epileptic seizure?",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of first seizure",
                "type": "date"
            }
        )
    )
    epilepsy_decimal_years = CharField(
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
