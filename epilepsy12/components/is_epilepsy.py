from django_unicorn.components import UnicornView

from epilepsy12.models import nonepilepsy
from ..models import DESSCRIBE, Registration
from ..constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, GENERALISED_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPTIC_SYNCOPES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, MIGRAINES, EPIS_MISC


class IsEpilepsyView(UnicornView):
    desscribe = DESSCRIBE.objects.none()
    case_id = ""
    registration = Registration.objects.none()
    focal_onset_other_details = ""
    epileptic_generalised_onset_other_details = ""

    # is epilepsy/nonepilepsy/other defaults
    epilepsyChoices = EPILEPSY_DIAGNOSIS_STATUS
    selected_epilepsy_status = epilepsyChoices[0][0]

    # epilepsy onset types and defaults (focal vs generalised)
    epileptic_seizure_onset_types = EPILEPSY_SEIZURE_TYPE

    # epilepsy seizure types and defaults (tonic vs tonic-clonic etc)
    epileptic_generalised_onset_types = GENERALISED_SEIZURE_TYPE

    # nonepilepsy types and defaults (syncopal vs behavioural etc)
    nonepileptic_seizure_types = NON_EPILEPSY_SEIZURE_TYPE
    nonepileptic_seizure_unknown_onset_types = NON_EPILEPSY_SEIZURE_ONSET

    # syncopal nonepilepsy types and defaults (vasovagal vs reflex anoxic etc)
    nonepileptic_syncopes = NON_EPILEPTIC_SYNCOPES

    # behavioural/psychological nonepilepsy
    nonepileptic_behavioural_psychological_symptoms = NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS

    # sleep
    nonepileptic_sleep_symptoms = NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS

    # paroxysm
    nonepileptic_paroxysms = NON_EPILEPSY_PAROXYSMS

    # migraine
    nonepileptic_migraines = MIGRAINES

    # misc
    miscellaneous_nonepilepsies = EPIS_MISC

    # def mount(self):
    #     return super().mount()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.case_id = kwargs.get("case_id")
        self.registration = kwargs.get("registration")

        if DESSCRIBE.objects.filter(
                registration=self.registration).exists():
            self.desscribe = DESSCRIBE.objects.filter(
                registration=self.registration).first()
            self.selected_epilepsy_status = self.desscribe.epilepsy_or_nonepilepsy_status
            self.focal_onset_other_details = self.desscribe.focal_onset_other_details

    def selectedStatus(self, selectedVal):
        """
        callback from epilepsy_or_nonepilepsy_status dropdown
        if epilepsy ('E'), then epileptic_seizure_onset component rendered: any previous selections are nullified/reset
        if nonepilepsy ('NE'), then nonepileptic_seizure_onset component rendered: any previous selections are nullified/reset
        if other ('U'), then no component rendered: any previous selections are nullified/reset
        """
        update_fields = {
            'epilepsy_or_nonepilepsy_status': selectedVal
        }

        if selectedVal == 'E' or selectedVal == 'U':
            update_fields['nonepileptic_seizure_unknown_onset'] = None
            update_fields['nonepileptic_seizure_unknown_onset_other_details'] = None
            update_fields['nonepileptic_seizure_syncope'] = None
            update_fields['nonepileptic_seizure_behavioural'] = None
            update_fields['nonepileptic_seizure_sleep'] = None
            update_fields['nonepileptic_seizure_paroxysmal'] = None
            update_fields['nonepileptic_seizure_migraine'] = None
            update_fields['nonepileptic_seizure_miscellaneous'] = None
            update_fields['nonepileptic_seizure_other'] = None
        if selectedVal == 'NE' or selectedVal == 'U':
            update_fields['focal_onset_impaired_awareness'] = False
            update_fields['focal_onset_automatisms'] = False
            update_fields['focal_onset_atonic'] = False
            update_fields['focal_onset_clonic'] = False
            update_fields['focal_onset_left'] = False
            update_fields['focal_onset_right'] = False
            update_fields['focal_onset_epileptic_spasms'] = False
            update_fields['focal_onset_hyperkinetic'] = False
            update_fields['focal_onset_myoclonic'] = False
            update_fields['focal_onset_tonic'] = False
            update_fields['focal_onset_autonomic'] = False
            update_fields['focal_onset_behavioural_arrest'] = False
            update_fields['focal_onset_cognitive'] = False
            update_fields['focal_onset_emotional'] = False
            update_fields['focal_onset_sensory'] = False
            update_fields['focal_onset_centrotemporal'] = False
            update_fields['focal_onset_temporal'] = False
            update_fields['focal_onset_frontal'] = False
            update_fields['focal_onset_parietal'] = False
            update_fields['focal_onset_occipital'] = False
            update_fields['focal_onset_gelastic'] = False
            update_fields['focal_onset_focal_to_bilateral_tonic_clonic'] = False
            update_fields['focal_onset_other'] = False
            update_fields['focal_onset_other_details'] = ""
            update_fields['generalised_onset'] = None
            update_fields['generalised_onset_other_details'] = None

        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=update_fields)
        self.selected_epilepsy_status = selectedVal

    # epileptic seizure onset callbacks
    def epilepsy_dropdown_change_select(self, selected_val, field_name):
        update_fields = {
            field_name: selected_val
        }
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=update_fields)

    # epileptic seizure focal callbacks
    def changeFocal(self, new_state, field_name):
        update_fields = {
            field_name: new_state
        }
        if field_name == 'focal_onset_other' and not new_state:
            update_fields['focal_onset_other_details'] = ''
            self.focal_onset_other_details = ''

        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=update_fields)

    # epileptic seizure focal input callback
    def focal_text_updated(self):
        print(self.focal_onset_other_details)
        DESSCRIBE.objects.update_or_create(registration=self.registration, defaults={
            'focal_onset_other_details': self.focal_onset_other_details
        })

    # generalised_other input callback
    def generalised_text_updated(self):
        DESSCRIBE.objects.update_or_create(registration=self.registration, defaults={
            'epileptic_generalised_onset_other_details': self.epileptic_generalised_onset_other_details
        })

    def changeNonepilepsySelect(self, selectedVal, field_name):
        # callback from select dropdown if nonepilepsy selected
        update_fields = {
            field_name: selectedVal
        }
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=update_fields)
