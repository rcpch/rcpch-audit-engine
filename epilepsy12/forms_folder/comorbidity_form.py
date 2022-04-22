from django.forms import CharField, ModelForm, ChoiceField

from epilepsy12.models.comorbidity import Comorbidity

from ..constants import *


class ComorbidityForm(ModelForm):
    comorbidity = ChoiceField(
        help_text="Select a comorbidity",
        choices=COMORBIDITIES
    )
    comorbidity_free_text = CharField(  # this is a free text field for 'other' diagnoses not included in the lists provided
        help_text="Please enter contextual information about the comorbidity",
        required=False
    )
    comorbidity_snomed_code = CharField(
        help_text="Please enter the SNOMED code for this comorbidity"
    )  # this is a new field - decision not to act on this currently: rare for a formal diagnosis to be give so

    class Meta:
        model = Comorbidity
        fields = [
            "comorbidity",
            "comorbidity_free_text",
            "comorbidity_snomed_code"
        ]
