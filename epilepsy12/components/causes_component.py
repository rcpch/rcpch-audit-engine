from django_unicorn.components import UnicornView

from epilepsy12.constants.causes import EPILEPSY_GENE_DEFECTS, EPILEPSY_GENETIC_CAUSE_TYPES, EPILEPSY_STRUCTURAL_CAUSE_TYPES, IMMUNE_CAUSES, METABOLIC_CAUSES
from ..models import DESSCRIBE, Registration
from ..constants import EPILEPSY_CAUSES


class CausesComponentView(UnicornView):
    case_id = ""
    registration = Registration.objects.none()
    desscribe = DESSCRIBE.objects.none()
    selected_seizure_cause_main = ""
    selected_structural_cause = ""
    selected_genetic_cause = ""
    selected_seizure_cause_gene_abnormality = ""
    selected_seizure_cause_genetic_other = ""
    seizure_cause_infectious = ""
    selected_seizure_cause_metabolic = ""
    seizure_cause_metabolic_other = ""
    selected_seizure_cause_immune = ""

    # main cause
    epilepsy_causes = EPILEPSY_CAUSES
    # structural causes
    structural_causes = EPILEPSY_STRUCTURAL_CAUSE_TYPES
    # genetic causes
    genetic_causes = EPILEPSY_GENETIC_CAUSE_TYPES
    # single gene defects
    gene_defects = EPILEPSY_GENE_DEFECTS
    # metabolic causes
    metabolic_causes = METABOLIC_CAUSES
    # immune causes
    immune_causes = IMMUNE_CAUSES

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        if (kwargs.get('registration')):
            self.registration = kwargs.get('registration')
            if DESSCRIBE.objects.filter(registration=self.registration).exists():
                self.desscribe = DESSCRIBE.objects.filter(
                    registration=self.registration).first()
                self.selected_seizure_cause_main = self.desscribe.seizure_cause_main
                self.selected_structural_cause = self.desscribe.seizure_cause_structural
                self.selected_genetic_cause = self.desscribe.seizure_cause_genetic
                self.selected_seizure_cause_gene_abnormality = self.desscribe.seizure_cause_gene_abnormality
                self.selected_seizure_cause_genetic_other = self.desscribe.seizure_cause_genetic_other
                self.seizure_cause_infectious = self.desscribe.seizure_cause_infectious
                self.seizure_cause_metabolic = self.desscribe.seizure_cause_metabolic
                self.seizure_cause_metabolic_other = self.desscribe.seizure_cause_metabolic_other
                self.selected_seizure_cause_immune = self.desscribe.seizure_cause_immune

    def epilepsy_dropdown_change_select(self, val, field_name):
        updated_field = {
            field_name: val
        }

        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults=updated_field)
        if field_name == "seizure_cause_main":
            self.selected_seizure_cause_main = val
        elif field_name == "seizure_cause_structural":
            self.selected_structural_cause = val
        elif field_name == "seizure_cause_genetic":
            self.selected_genetic_cause = val
        elif field_name == "seizure_cause_gene_abnormality":
            self.selected_seizure_cause_gene_abnormality = val
        elif field_name == "seizure_cause_metabolic":
            self.selected_seizure_cause_metabolic = val
        elif field_name == "seizure_cause_immune":
            self.selected_seizure_cause_immune = val
        else:
            return

    def change_seizure_cause_genetic_other(self):
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults={
                'seizure_cause_genetic_other': self.seizure_cause_genetic_other
            })

    def change_seizure_cause_infectious(self):
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults={
                'seizure_cause_infectious': self.seizure_cause_infectious
            })

    def change_seizure_cause_metabolic_other(self):
        self.desscribe = DESSCRIBE.objects.update_or_create(
            registration=self.registration, defaults={
                'seizure_cause_metabolic_other': self.seizure_cause_metabolic_other
            })
