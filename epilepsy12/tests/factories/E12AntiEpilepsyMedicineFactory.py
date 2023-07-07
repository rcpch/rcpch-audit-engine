"""Factory fn to create new E12 AntiEpilepsyMedicine, related to a management.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    AntiEpilepsyMedicine,
    MedicineEntity,
)


class E12AntiEpilepsyMedicineFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Management.

    This Factory is generated AFTER a Management generated.
    """

    class Meta:
        model = AntiEpilepsyMedicine

    # Once Management instance made, it will attach to this instance
    management = None

    # is_rescue_medicine = False

    # medicine_entity = factory.lazy_attribute(
    #     lambda _: MedicineEntity.objects.get(medicine_name="Sodium valproate")
    # )
    # antiepilepsy_medicine_risk_discussed = True

    # # Once a AntiEpilepsyMedicine is made, set antiepilepsy_medicine_start_date as 28 days after registration date
    # @factory.lazy_attribute
    # def antiepilepsy_medicine_start_date(self):
    #     return self.management.registration.registration_date + timedelta(days=28)

    # # Sodium Valproate for females of child bearing age
    # @factory.LazyAttribute
    # def is_a_pregnancy_prevention_programme_needed(self):
    #     # check if aed is valproate
    #     if self.medicine_entity.medicine_name != "Sodium valproate":
    #         return None

    #     # check if female
    #     if self.management.registration.case.sex != 2:
    #         return None

    #     # check if age when starting valproate is >= 12
    #     age_when_starting_aed_in_years = (
    #         self.antiepilepsy_medicine_start_date
    #         - self.management.registration.case.date_of_birth
    #     ).days // 365

    #     if not (age_when_starting_aed_in_years >= 12):
    #         return None

    #     # return True if taking valproate, female, and started when of child bearing age
    #     return True

    # # Sodium Valproate for females of child bearing age
    # @factory.LazyAttribute
    # def has_a_valproate_annual_risk_acknowledgement_form_been_completed(self):
    #     # check if aed is valproate
    #     if self.medicine_entity.medicine_name != "Sodium valproate":
    #         return None

    #     # check if female
    #     if self.management.registration.case.sex != 2:
    #         return None

    #     # check if age when starting valproate is >= 12
    #     age_when_starting_aed_in_years = (
    #         self.antiepilepsy_medicine_start_date
    #         - self.management.registration.case.date_of_birth
    #     ).days // 365

    #     if not (age_when_starting_aed_in_years >= 12):
    #         return None

    #     # return True if taking valproate, female, and started when of child bearing age
    #     return True

    # # Sodium Valproate for females of child bearing age
    # @factory.LazyAttribute
    # def is_a_pregnancy_prevention_programme_in_place(self):
    #     # check if aed is valproate
    #     if self.medicine_entity.medicine_name != "Sodium valproate":
    #         return None

    #     # check if female
    #     if self.management.registration.case.sex != 2:
    #         return None

    #     # check if age when starting valproate is >= 12
    #     age_when_starting_aed_in_years = (
    #         self.antiepilepsy_medicine_start_date
    #         - self.management.registration.case.date_of_birth
    #     ).days // 365

    #     if not (age_when_starting_aed_in_years >= 12):
    #         return None

    #     # return True if taking valproate, female, and started when of child bearing age
    #     return True

