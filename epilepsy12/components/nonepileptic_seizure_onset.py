from django_unicorn.components import UnicornView

from epilepsy12.models import nonepilepsy
from ..forms_folder.multiaxial_description_form import MultiaxialDescriptionForm
from ..models import DESSCRIBE
from ..constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, GENERALISED_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE


class NonepilepticSeizureOnsetView(UnicornView):
    case_id = ""
    registration = None
    desscribe = DESSCRIBE.objects.none()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        if (kwargs.get('registration')):
            self.registration = kwargs.get('registration')
            if DESSCRIBE.objects.filter(registration=self.registration).exists():
                self.desscribe = DESSCRIBE.objects.filter(
                    registration=self.registration).first()
