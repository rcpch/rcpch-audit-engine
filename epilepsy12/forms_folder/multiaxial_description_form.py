from django import forms
from django.forms import ModelForm
from epilepsy12.models.desscribe import DESSCRIBE


class MultiaxialDescriptionForm(ModelForm):

    relevant_impairments_behavioural_educational = forms.CheckboxInput(
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MultiaxialDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['description_keywords'].widget.attrs = {
            'type': 'text',
            'placeholder': 'Description',
            'class': 'prompt'
        }

    class Meta:
        model = DESSCRIBE
        fields = [
            'description',
            'description_keywords',
            'epilepsy_status',
            'seizure_type',
            'syndrome',
            'cause',
            'relevant_impairments_behavioural_educational'
        ]
