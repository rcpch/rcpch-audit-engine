from django import forms
from ..models import Case
from ..constants import *


class CaseForm(forms.ModelForm):
    first_name = forms.CharField(
        help_text="Enter the first name.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "first name"
            }
        )
    )
    surname = forms.CharField(
        help_text="Enter the surname.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "surname"
            }
        )
    )
    date_of_birth = forms.DateField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "date of birth",
                "type": "date"
            }
        )
    )
    gender = forms.ChoiceField(
        choices=SEX_TYPE,
        widget=forms.Select(),
        required=True
    )
    nhs_number = forms.CharField(
        help_text="Enter the NHS Number. This is 10 digits long.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "NHS Number",
                "type": "text"
            }
        )
    )
    postcode = forms.CharField(
        help_text="Enter the postcode.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Postcode",
                "type": "text"
            }
        )
    )
    ethnicity = forms.ChoiceField(
        help_text="Enter the ethnicity",
        choices=ETHNICITIES,
        widget=forms.Select(),
        required=True
    ),
    locked = forms.CheckboxInput(
    ),
    locked_at = forms.DateTimeField(
        help_text="Time record locked.",
        required=False
    )
    locked_by = forms.CharField(
        help_text="User who locked the record",
        required=False
    )

    class Meta:
        model = Case
        fields = [
            'first_name', 'surname', 'date_of_birth', 'gender', 'nhs_number', 'postcode', 'ethnicity', 'locked', 'locked_at'
        ]
        exclude = ['locked_by']
