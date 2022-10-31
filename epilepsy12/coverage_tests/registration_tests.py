from datetime import date
from django.test import TestCase
from ..models import AuditProgress, Case, Registration


class RegistrationTests(TestCase):

    def setUp(self) -> None:
        case = Case.objects.create(
            nhs_number=2345456123,
            first_name="Fyodor",
            surname="Dostoyevsky",
            gender=1,
            date_of_birth=date(2009, 11, 5),
            postcode="WC1X 8SH",
            locked=False,
            ethnicity="A"
        )
        audit_progress = AuditProgress.objects.create(
            registration_complete=False,
            first_paediatric_assessment_complete=False,
            assessment_complete=False,
            epilepsy_context_complete=False,
            multiaxial_diagnosis_complete=False,
            management_complete=False,
            investigations_complete=False,
            registration_total_expected_fields=4,
            registration_total_completed_fields=0,
            first_paediatric_assessment_total_expected_fields=0,
            first_paediatric_assessment_total_completed_fields=0,
            assessment_total_expected_fields=0,
            assessment_total_completed_fields=0,
            epilepsy_context_total_expected_fields=0,
            epilepsy_context_total_completed_fields=0,
            multiaxial_diagnosis_total_expected_fields=0,
            multiaxial_diagnosis_total_completed_fields=0,
            investigations_total_expected_fields=0,
            investigations_total_completed_fields=0,
            management_total_expected_fields=0,
            management_total_completed_fields=0
        )
        Registration.objects.create(
            case=case,
            audit_progress=audit_progress
        )

    def test_initial_values_none(self):
        c = Case.objects.filter(surname="Dostoyevsky").get()
        r = Registration.objects.filter(case=c).get()

        self.assertEqual(
            r.eligibility_criteria_met,
            None
        )

        self.assertEqual(
            r.registration_close_date,
            None
        )

        self.assertEqual(
            r.registration_date,
            None
        )

        self.assertEqual(
            r.cohort,
            None
        )
