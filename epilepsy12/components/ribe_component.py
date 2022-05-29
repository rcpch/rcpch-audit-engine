from django_unicorn.components import UnicornView
from ..models import DESSCRIBE, Registration, Comorbidity


class RibeComponentView(UnicornView):
    case_id = ""
    registration = Registration.objects.none()
    desscribe = DESSCRIBE.objects.none()
    selected_relevant_impairments_behavioural_educational = False
    comorbidities = Comorbidity.objects.none()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        if kwargs.get('case_id'):
            self.case_id = kwargs.get('case_id')
            if Comorbidity.objects.filter(case_id=self.case_id).exists():
                self.comorbidities = Comorbidity.objects.filter(
                    case_id=self.case_id)
        if kwargs.get('registration'):
            self.registration = kwargs.get('registration')
            if DESSCRIBE.objects.filter(registration=self.registration).exists():
                self.desscribe = DESSCRIBE.objects.filter(
                    registration=self.registration).first()
                self.selected_relevant_impairments_behavioural_educational = self.desscribe.relevant_impairments_behavioural_educational

    def changeRIBE(self, val, field_name):
        updated_field = {
            field_name: val
        }
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=updated_field)
        self.selected_relevant_impairments_behavioural_educational = val
