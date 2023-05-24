"""Factory fn to create new E12 EpilepsyContext

NOTE: calling this factory will cause dependencies to be created automatically e.g. Registration, Case related to an Organisation.
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    EpilepsyContext
)
from epilepsy12.constants import OPT_OUT_UNCERTAIN

class E12EpilepsyContextFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EpilepsyContext
    
    # when a registration instance created, it will attach to this instance
    registration = None
    
    previous_febrile_seizure=OPT_OUT_UNCERTAIN[0][0]
    previous_acute_symptomatic_seizure=OPT_OUT_UNCERTAIN[0][0]
    is_there_a_family_history_of_epilepsy=OPT_OUT_UNCERTAIN[0][0]
    previous_neonatal_seizures=OPT_OUT_UNCERTAIN[0][0]
    diagnosis_of_epilepsy_withdrawn=True
    were_any_of_the_epileptic_seizures_convulsive=True
    experienced_prolonged_generalized_convulsive_seizures=OPT_OUT_UNCERTAIN[0][0]
    experienced_prolonged_focal_seizures=OPT_OUT_UNCERTAIN[0][0]