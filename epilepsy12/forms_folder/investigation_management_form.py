from django.forms import CharField, CheckboxInput, ModelForm, ChoiceField, DateField, TextInput
from epilepsy12.models.investigation_management import Investigation_Management

# from epilepsy12.models.investigations import Investigations
# from epilepsy12.models.rescue_medicine import RescueMedicine


from ..constants import *


# class InvestigationForm(ModelForm):
#     eeg_indicated = CheckboxInput(
#         # "Is an EEG indicated?"
#     )
#     eeg_request_date = DateField(
#         help_text="When was an EEG requested?",
#         widget=TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Date EEG requested",
#                 "type": "date"
#             }
#         )
#     )
#     eeg_performed_date = DateField(
#         help_text="Date EEG performed",
#         widget=TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Date EEG performed",
#                 "type": "date"
#             }
#         )
#     )
#     twelve_lead_ecg_status = CheckboxInput(
#         # Has ECG been done?
#     )
#     ct_head_scan_status = CheckboxInput(
#         # Has CT Head been done?
#     )
#     mri_brain_date = DateField(
#         # has MRI brain been done?
#         help_text="Date MRI Brain performed",
#         widget=TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Date MRI brain performed",
#                 "type": "date"
#             }
#         )
#     )

#     class Meta:
#         model = Investigations
#         fields = [
#             'eeg_indicated',
#             'eeg_request_date',
#             'eeg_performed_date',
#             'twelve_lead_ecg_status',
#             'ct_head_scan_status',
#             'mri_brain_date'
#         ]


# class MedicationForm(ModelForm):
#     rescue_medicine_type = ChoiceField(
#         help_text="Type of rescue medicine prescribed",
#         choices=BENZODIAZEPINE_TYPES
#     )
#     rescue_medicine_other = CharField(
#         help_text="Other documented rescue medicine previously not specified.",
#     )
#     rescue_medicine_start_date = DateField(
#         help_text="date rescue medicine prescribed/given.",
#         widget=TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Date rescue medicine given/prescribed",
#                 "type": "date"
#             }
#         )
#     )
#     rescue_medicine_stop_date = DateField(
#         help_text="date rescue medicine stopped if known.",
#         widget=TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Date rescue medicine stopped if known.",
#                 "type": "date"
#             }
#         )
#     )
#     rescue_medicine_status = CheckboxInput(
#         # "status of rescue medicine prescription."
#     )
#     rescue_medicine_notes = CharField(
#         help_text="additional notes relating to rescue medication.",
#     )

#     class Meta:
#         model = RescueMedicine
#         fields = [
#             'rescue_medicine_type',
#             'rescue_medicine_other',
#             'rescue_medicine_start_date',
#             'rescue_medicine_stop_date',
#             'rescue_medicine_status',
#             'rescue_medicine_notes',
#         ]


class InvestigationManagementForm(ModelForm):
    eeg_indicated = CheckboxInput(
        # "Is an EEG indicated?"
    )
    eeg_request_date = DateField(
        help_text="When was an EEG requested?",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date EEG requested",
                "type": "date"
            }
        )
    )
    eeg_performed_date = DateField(
        help_text="Date EEG performed",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date EEG performed",
                "type": "date"
            }
        )
    )
    twelve_lead_ecg_status = CheckboxInput(
        # Has ECG been done?
    )
    ct_head_scan_status = CheckboxInput(
        # Has CT Head been done?
    )
    mri_brain_date = DateField(
        # has MRI brain been done?
        help_text="Date MRI Brain performed",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date MRI brain performed",
                "type": "date"
            }
        )
    )

    rescue_medicine_type = ChoiceField(
        help_text="Type of rescue medicine prescribed",
        choices=BENZODIAZEPINE_TYPES
    )
    rescue_medicine_other = CharField(
        help_text="Other documented rescue medicine previously not specified.",
    )
    rescue_medicine_start_date = DateField(
        help_text="date rescue medicine prescribed/given.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date rescue medicine given/prescribed",
                "type": "date"
            }
        )
    )
    rescue_medicine_stop_date = DateField(
        help_text="date rescue medicine stopped if known.",
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date rescue medicine stopped if known.",
                "type": "date"
            }
        )
    )
    rescue_medicine_status = CheckboxInput(
        # "status of rescue medicine prescription."
    )
    rescue_medicine_notes = CharField(
        help_text="additional notes relating to rescue medication.",
    )

    class Meta:
        model = Investigation_Management
        fields = [
            'eeg_indicated',
            'eeg_request_date',
            'eeg_performed_date',
            'twelve_lead_ecg_status',
            'ct_head_scan_status',
            'mri_brain_date',
            'rescue_medicine_type',
            'rescue_medicine_other',
            'rescue_medicine_start_date',
            'rescue_medicine_stop_date',
            'rescue_medicine_status',
            'rescue_medicine_notes',
        ]
