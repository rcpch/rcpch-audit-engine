from django.forms import CharField, CheckboxInput, ModelForm, ChoiceField, DateField, TextInput
from epilepsy12.models.desscribe import DESSCRIBE


class MultiaxialDescriptionForm(ModelForm):

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
        ]
