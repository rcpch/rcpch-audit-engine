from django_unicorn.components import UnicornView

from epilepsy12.models import nonepilepsy
from ..forms_folder.multiaxial_description_form import MultiaxialDescriptionForm
from ..models import DESSCRIBE
from ..constants.epilepsy_types import EPILEPSY_DIAGNOSIS_STATUS
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, GENERALISED_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE


class EpilepticSeizureOnsetView(UnicornView):
    case_id = ""
    registration = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(**kwargs)  # calling super is required
    #     self.case_id = kwargs.get("case_id")
    #     self.registration = kwargs.get("registration")

    def mount(self):
        print("I have mounted")
