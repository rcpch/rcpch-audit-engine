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

    class Params:
        pass_mental_health_support = factory.Trait(
            has_support_for_mental_health_support=True
        )
        fail_mental_health_support = factory.Trait(
            has_support_for_mental_health_support=False
        )

    # Once Registration instance made, it will attach to this instance
    registration = None

    @factory.post_generation
    def antiepilepsymedicine(self, create, extracted, **kwargs):
        # default don't create any AEM
        if not create:
            return

        print(f"{extracted=}")
        print(f"{kwargs=}")
        if kwargs:
            
            if 'sodium_valproate' in kwargs:
                # create a related Valproate AEM instance, with pregnancy prevention fields set depending on sodium_valproate flag.
                self.has_an_aed_been_given = True
                
                if kwargs['sodium_valproate'] == 'pass':

                    E12AntiEpilepsyMedicineFactory(
                        management=self,
                        is_rescue_medicine=False,
                        medicine_entity=MedicineEntity.objects.get(
                            medicine_name="Sodium valproate"
                        ),
                        antiepilepsy_medicine_risk_discussed=True,
                        is_a_pregnancy_prevention_programme_needed=True,
                        has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
                    )
                elif kwargs['sodium_valproate'] == 'fail':
                    E12AntiEpilepsyMedicineFactory(
                        management=self,
                        is_rescue_medicine=False,
                        medicine_entity=MedicineEntity.objects.get(
                            medicine_name="Sodium valproate"
                        ),
                        antiepilepsy_medicine_risk_discussed=False,
                        is_a_pregnancy_prevention_programme_needed=False,
                        has_a_valproate_annual_risk_acknowledgement_form_been_completed=False,
                    )
