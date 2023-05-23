"""Factory fn to create new E12 Management, related to a created Registration.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Management
from .E12AntiEpilepsyMedicineFactory import E12AntiEpilepsyMedicineFactory

from epilepsy12.models import (
    MedicineEntity,
)

class E12ManagementFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Management.

    This Factory is generated AFTER a Registration is created.

    Default:
        - aed will be sodium valproate, with pregnancy fields automatically filled as True if childbearing age girl
    """

    class Meta:
        model = Management

    # Once Registration instance made, it will attach to this instance
    registration = None

    has_an_aed_been_given = True
    aed = factory.RelatedFactory(
        E12AntiEpilepsyMedicineFactory,
        factory_related_name="management"
    )

    has_rescue_medication_been_prescribed = True
    rescue_med = factory.RelatedFactory(
        E12AntiEpilepsyMedicineFactory, 
        factory_related_name="management",
        is_rescue_medicine = True,
        medicine_entity=factory.lazy_attribute(
                lambda _: MedicineEntity.objects.get(medicine_name="Lorazepam")
            ),
    )
    
    individualised_care_plan_in_place = True

    # Once a Management is made, set individualised_care_plan_date as 28 days after registration date
    @factory.lazy_attribute
    def individualised_care_plan_date(self):
        return self.registration.registration_date + timedelta(days=28)

    individualised_care_plan_has_parent_carer_child_agreement = True
    individualised_care_plan_includes_service_contact_details = True
    individualised_care_plan_include_first_aid = True
    individualised_care_plan_parental_prolonged_seizure_care = True
    individualised_care_plan_includes_general_participation_risk = True
    individualised_care_plan_addresses_water_safety = True
    individualised_care_plan_addresses_sudep = True
    individualised_care_plan_includes_ehcp = True
    has_individualised_care_plan_been_updated_in_the_last_year = True
    has_been_referred_for_mental_health_support = True
    has_support_for_mental_health_support = True
