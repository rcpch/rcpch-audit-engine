from email.policy import default
from django.forms import BaseInlineFormSet, ModelForm, CheckboxInput, DateField, TextInput

from epilepsy12.models.assessment import Assessment

from ..constants import *


class AssessmentForm(ModelForm):

    has_an_aed_been_given = CheckboxInput(
        #  help_text="Has an antiepilepsy medicine been prescribed?",
    )
    rescue_medication_prescribed = CheckboxInput(
        #  help_text="Has a rescue medicine been prescribed?",
    )
    childrens_epilepsy_surgical_service_referral_criteria_met = CheckboxInput(
        #  help_text="Has a referral been made to a consultant paediatrician with an interest in epilepsy?",
    )
    consultant_paediatrician_referral_made = CheckboxInput(
        #  help_text="Have the criteria for referral to a children's epilepsy surgery service been met?",
    )
    consultant_paediatrician_referral_date = DateField(
        help_text="Date of referral to a consultant paediatrician with an interest in epilepsy.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of referral to a consultant paediatrician with an interest in epilepsy.",
                "type": "date"
            }
        )
    )
    consultant_paediatrician_input_date = DateField(
        help_text="Date seen by a consultant paediatrician with an interest in epilepsy.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date seen by a consultant paediatrician with an interest in epilepsy.",
                "type": "date"
            }
        )
    )
    paediatric_neurologist_referral_made = CheckboxInput(
        #  help_text="Has a referral to a consultant paediatric neurologist been made?",
    )
    paediatric_neurologist_referral_date = DateField(
        help_text="Date of referral to a consultant paediatric neurologist.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of referral to a consultant paediatric neurologist.",
                "type": "date"
            }
        )
    )
    paediatric_neurologist_input_date = DateField(
        help_text="Date seen by consultant paediatric neurologist.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date seen by consultant paediatric neurologist.",
                "type": "date"
            }
        )
    )
    childrens_epilepsy_surgical_service_referral_date = DateField(
        help_text="Date of referral to a children's epilepsy surgery service",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of referral to a children's epilepsy surgery service",
                "type": "date"
            }
        )
    )
    childrens_epilepsy_surgical_service_input_date = DateField(
        help_text="Date seen by children's epilepsy surgery service",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date seen by children's epilepsy surgery service",
                "type": "date"
            }
        )
    )
    were_any_of_the_epileptic_seizures_convulsive = CheckboxInput(
        #  help_text="Were any of the epileptic seizures convulsive?",
    )
    prolonged_generalized_convulsive_seizures = CheckboxInput(
        #  help_text="Were there any prolonged generalised epileptic seizures?",
    )
    experienced_prolonged_focal_seizures = CheckboxInput(
        #  help_text="Were there any prolonged focal seizures?",
    )
    has_an_aed_been_given = CheckboxInput(
        #  help_text="Has an antiepilepsy medicine been given?",
    )
    paroxysmal_episode = CheckboxInput(
        #  help_text="Were any episodes paroxysmal?",
    )

    class Meta:
        model = Assessment
        fields = [
            'has_an_aed_been_given',
            'rescue_medication_prescribed',
            'childrens_epilepsy_surgical_service_referral_criteria_met',
            'consultant_paediatrician_referral_made',
            'consultant_paediatrician_referral_date',
            'consultant_paediatrician_input_date',
            'paediatric_neurologist_referral_made',
            'paediatric_neurologist_referral_date',
            'paediatric_neurologist_input_date',
            'childrens_epilepsy_surgical_service_referral_date',
            'childrens_epilepsy_surgical_service_input_date',
            'were_any_of_the_epileptic_seizures_convulsive',
            'prolonged_generalized_convulsive_seizures',
            'experienced_prolonged_focal_seizures',
            'has_an_aed_been_given',
            'paroxysmal_episode'
        ]


class AssessmentInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # example custom validation across forms in the formset
        for form in self.forms:
            # your custom formset validation
            print("hello")
