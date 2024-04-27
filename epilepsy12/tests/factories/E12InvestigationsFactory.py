"""Factory fn to create new E12 Investigations, related to a created Registration.
"""

# standard imports
from datetime import date

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Investigations


class E12InvestigationsFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Investigations.

    This Factory is generated AFTER a Registration is created.


    """

    class Meta:
        model = Investigations

    # Once Registration instance made, it will attach to this instance
    registration = None

    class Params:
        pass_ecg = factory.Trait(
            twelve_lead_ecg_status=True,
        )
        fail_ecg = factory.Trait(
            twelve_lead_ecg_status=False,
        )
        pass_mri = factory.Trait(
            mri_indicated=True,
            mri_brain_requested_date=date(2023, 2, 1),
            mri_brain_reported_date=date(2023, 2, 2),  # 1 day later
        )
        fail_mri = factory.Trait(
            mri_indicated=True,
            mri_brain_requested_date=date(2023, 2, 1),
            mri_brain_reported_date=date(2023, 5, 1),  # 3 months later (>42 days)
        )
