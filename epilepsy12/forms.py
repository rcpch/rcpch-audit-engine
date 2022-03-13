from django import forms
from .models import Case
from .constants import *


class CaseForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "first name"
            }
        )
    )
    surname = forms.CharField(
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
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "NHS Number",
                "type": "text"
            }
        )
    )
    postcode = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Postcode",
                "type": "text"
            }
        )
    )

    class Meta:
        model = Case
        fields = [
            'first_name', 'surname', 'date_of_birth', 'gender', 'nhs_number', 'postcode'
        ]
