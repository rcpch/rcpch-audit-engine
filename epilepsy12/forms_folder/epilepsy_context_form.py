from django import forms

from epilepsy12.models.epilepsy_context import EpilepsyContext
from epilepsy12.models.comorbidity import Comorbidity

from ..constants import *


class EpilepsyContextForm(forms.ModelForm):

    previous_febrile_seizure = forms.ChoiceField(
        help_text="has there been a previous febrile seizure?",
        choices=OPT_OUT_UNCERTAIN
    )
    previous_acute_symptomatic_seizure = forms.ChoiceField(
        help_text="has there been a previous acute symptomatic seizure?",
        choices=OPT_OUT_UNCERTAIN
    )
    is_there_a_family_history_of_epilepsy = forms.ChoiceField(
        help_text="is there a family history of epilepsy?",
        choices=OPT_OUT_UNCERTAIN
    )
    previous_neonatal_seizures = forms.ChoiceField(
        help_text="were there seizures in the neonatal period?",
        choices=OPT_OUT_UNCERTAIN
    )
    diagnosis_of_epilepsy_withdrawn = forms.ChoiceField(
        help_text="has the diagnosis of epilepsy been withdrawn?",
        choices=OPT_OUT
    )
    date_of_first_epileptic_seizure = forms.DateField(
        help_text="What date was the first reported epileptic seizure?"
    )

    class Meta:
        model = EpilepsyContext
        fields = [

        ]
# date_of_initial_assessment = forms.DateField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "registration date",
#                 "type": "date"
#             }
#         )
#     )
# neurological_examination_performed = forms.CheckboxInput(
#         # "has a neurological examination been performed?"
#         check_test=True
#     )
# first_paediatric_assessment_in_acute_or_nonacute_setting = forms.ChoiceField(
#         help_text="Is the first paediatric assessment in an acute or nonacute setting?",
#         widget=forms.Select(),
#         required=True,
#         choices=CHRONICITY
#     )
