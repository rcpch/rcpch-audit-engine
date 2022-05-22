from django_unicorn.components import UnicornView

from epilepsy12.models import nonepilepsy
from ..forms_folder.multiaxial_description_form import MultiaxialDescriptionForm
from ..models import DESSCRIBE, Registration
from ..constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, GENERALISED_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPTIC_SYNCOPES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, MIGRAINES, EPIS_MISC


class IsEpilepsyView(UnicornView):
    desscribe = DESSCRIBE.objects.none()
    case_id = ""
    registration = Registration.objects.none()

    # form = MultiaxialDescriptionForm(request.POST or None)
    epilepsyChoices = EPILEPSY_DIAGNOSIS_STATUS
    selected_epilepsy_status = epilepsyChoices[0][0]

    # epilepsy
    epileptic_seizure_onset_types = EPILEPSY_SEIZURE_TYPE
    selected_epileptic_seizure_onset_type = epileptic_seizure_onset_types[0][0]

    epileptic_generalised_onset_types = GENERALISED_SEIZURE_TYPE
    selected_epileptic_generalised_onset_type = epileptic_generalised_onset_types[0][0]

    # nonepilepsy
    nonepileptic_seizure_onset_types = NON_EPILEPSY_SEIZURE_ONSET
    selected_nonepileptic_seizure_onset_type = nonepileptic_seizure_onset_types[0][0]

    nonepileptic_seizure_types = NON_EPILEPSY_SEIZURE_TYPE
    selected_nonepileptic_seizure_type = nonepileptic_seizure_types[0][0]

    # syncopal nonepilepsy
    nonepileptic_syncopes = NON_EPILEPTIC_SYNCOPES
    selected_nonepileptic_syncope = nonepileptic_syncopes[0][0]

    # behavioural/psychological nonepilepsy
    nonepileptic_behavioural_psychological_symptoms = NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS
    selected_nonepileptic_behavioural_psychological_symptom = nonepileptic_behavioural_psychological_symptoms[
        0][0]

    # sleep
    nonepileptic_sleep_symptoms = NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS
    selected_nonepileptic_sleep_symptom = nonepileptic_sleep_symptoms[0][0]

    # paroxysm
    nonepileptic_paroxysms = NON_EPILEPSY_PAROXYSMS
    selected_nonepileptic_paroxysm = nonepileptic_paroxysms[0][0]

    # migraine
    nonepileptic_migraines = MIGRAINES
    selected_nonepileptic_migraine = nonepileptic_migraines[0][0]

    # misc
    miscellaneous_nonepilepsies = EPIS_MISC
    selected_miscellaneous_nonepilepsy = miscellaneous_nonepilepsies[0][0]

    def mount(self):
        return super().mount()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.case_id = kwargs.get("case_id")
        self.registration = kwargs.get("registration")

        try:
            self.desscribe = DESSCRIBE.objects.filter(
                registration=self.registration).first()
            self.selected_epilepsy_status = self.desscribe.epilepsy_or_nonepilepsy_status
        except:
            self.desscribe = None

    def selectedStatus(self, selectedVal):
        self.desscribe = DESSCRIBE.objects.update_or_create(registration=self.registration, defaults={
            'epilepsy_or_nonepilepsy_status': selectedVal
        })
        self.selected_epilepsy_status = selectedVal

    def changedEpilepticSeizureOnsetType(self, selectedVal):
        self.selected_epileptic_seizure_onset_type = selectedVal

    def selectedEpilepticSeizureGeneralisedOnset(self, selectedVal):
        self.selected_epileptic_generalised_onset_type = selectedVal

    def changedSyncopalNonepilepsy(self, selectedVal):
        self.selected_nonepileptic_syncope = selectedVal

    # class Meta:
    #     javascript_exclude = ('epilepsyChoices', 'epileptic_seizure_types', 'epileptic_generalised_onset_types',
    #                           'nonepileptic_seizure_onset_types', 'nonepileptic_seizure_types,')
