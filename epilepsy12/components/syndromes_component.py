from django_unicorn.components import UnicornView
from ..models import DESSCRIBE, Registration
from ..constants import SYNDROMES


class SyndromesComponentView(UnicornView):
    case_id = ""
    registration = Registration.objects.none()
    desscribe = DESSCRIBE.objects.none()

    # syndromes
    syndromes = SYNDROMES

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        if (kwargs.get('registration')):
            self.registration = kwargs.get('registration')
            if DESSCRIBE.objects.filter(registration=self.registration).exists():
                self.desscribe = DESSCRIBE.objects.filter(
                    registration=self.registration).first()

    def change_syndrome_select(self, selected_val):
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults={
                'syndrome': selected_val
            })
