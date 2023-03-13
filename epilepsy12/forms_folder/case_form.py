from django import forms
from ..models import Case
from ..constants import *


class CaseForm(forms.ModelForm):
    unknown_postcode = forms.CharField()

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
    sex = forms.ChoiceField(
        choices=SEX_TYPE,
        widget=forms.Select(attrs={'class': 'ui rcpch dropdown'}),
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
        ),
        required=False
    )
    ethnicity = forms.ChoiceField(
        choices=ETHNICITIES,
        widget=forms.Select(
            attrs={
                'class': 'ui rcpch dropdown'
            }
        ),
        required=True
    )
    locked_at = forms.DateTimeField(
        help_text="Time record locked.",
        required=False
    )
    locked_by = forms.CharField(
        help_text="User who locked the record",
        required=False
    )

    def __init__(self, *args, **kwargs) -> None:
        super(CaseForm, self).__init__(*args, **kwargs)
        self.fields['ethnicity'].widget.attrs.update({
            'class': 'ui rcpch dropdown'
        })

    class Meta:
        model = Case
        fields = [
            'first_name', 'surname', 'date_of_birth', 'sex', 'nhs_number', 'postcode', 'ethnicity', 'unknown_postcode'
        ]

    def clean(self):
        cleaned_data = super(CaseForm, self).clean()

        if (len(self.cleaned_data['unknown_postcode']) > 0 and len(self.cleaned_data['postcode']) == 0):
            self.cleaned_data['postcode'] = self.cleaned_data['unknown_postcode']
        # Finally, return the cleaned_data
        return cleaned_data
