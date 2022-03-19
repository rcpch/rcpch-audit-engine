from django import forms

from epilepsy12.models.initial_assessment import InitialAssessment
from ..constants import *


class InitialAssessmentForm(forms.ModelForm):
    date_of_initial_assessment = forms.DateField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "registration date",
                "type": "date"
            }
        )
    )
    date_of_referral_to_general_paediatrics = forms.DateField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "registration date",
                "type": "date"
            }
        )
    )
    first_paediatric_assessment_in_acute_or_nonacute_setting = forms.ChoiceField(
        help_text="Is the first paediatric assessment in an acute or nonacute setting?",
        widget=forms.Select(),
        required=True,
        choices=CHRONICITY
    )
    has_description_of_the_episode_or_episodes_been_gathered = forms.CheckboxInput(
        # "has a description of the episode or episodes been gathered?",
        check_test=True
    )
    when_the_first_epileptic_episode_occurred_confidence = forms.ChoiceField(
        help_text="how accurate is the date of the first epileptic episode?",
        choices=DATE_ACCURACY
    )
    when_the_first_epileptic_episode_occurred = forms.DateField(
        help_text="what is the date that the first epileptic episode occurred?",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "registration date",
                "type": "date"
            }
        )
    )
    has_number_of_episodes_since_the_first_been_documented = forms.CheckboxInput(
        # "has the frequency of episodes since the first recorded been documented?",
        check_test=True
    )
    general_examination_performed = forms.CheckboxInput(
        # "has a general clinical examination been performed?"
        check_test=True
    )
    neurological_examination_performed = forms.CheckboxInput(
        # "has a neurological examination been performed?"
        check_test=True
    )
    developmental_learning_or_schooling_problems = forms.CheckboxInput(
        # "has the presence or absence of developmental, learning or school-based problems been recorded?"
        check_test=True
    )
    behavioural_or_emotional_problems = forms.CheckboxInput(
        # "are there any behaviour or emotional comorbid conditions present?"
        check_test=True
    )
    diagnostic_status = forms.ChoiceField(  # This currently essential - used to exclude nonepilepic kids
        choices=DIAGNOSTIC_STATUS,
        help_text="Status of epilepsy diagnosis. Must have epilepsy or probable epilepsy to be included.",
        required=True
    )

    class Meta:
        model = InitialAssessment
        fields = [
            'date_of_initial_assessment',
            'date_of_referral_to_general_paediatrics',
            'first_paediatric_assessment_in_acute_or_nonacute_setting',
            'has_description_of_the_episode_or_episodes_been_gathered',
            'when_the_first_epileptic_episode_occurred_confidence',
            'when_the_first_epileptic_episode_occurred',
            'has_number_of_episodes_since_the_first_been_documented',
            'general_examination_performed',
            'neurological_examination_performed',
            'developmental_learning_or_schooling_problems',
            'behavioural_or_emotional_problems',
            'diagnostic_status'
        ]
