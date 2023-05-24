"""Factory fn to create new E12 Assessments, related to a created Registration.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Assessment


class E12AssessmentFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Registration.

    This Factory is generated AFTER a Registration is created.

    Default:
        - consultant_paediatrician_referral_date is 28 days after registration
        - consultant_paediatrician_input_date is 5 days after referral date
        - 
    """

    class Meta:
        model = Assessment

    # Once Registration instance made, it will attach to this instance
    registration = None

    childrens_epilepsy_surgical_service_referral_criteria_met = True
    consultant_paediatrician_referral_date = factory.lazy_attribute(lambda assessment: assessment.registration.registration_date + timedelta(days=28))
    consultant_paediatrician_input_date = factory.lazy_attribute(lambda assessment: assessment.consultant_paediatrician_referral_date + timedelta(days=5))
    
    consultant_paediatrician_referral_made = True
    paediatric_neurologist_referral_made = True
    childrens_epilepsy_surgical_service_referral_made = True
    epilepsy_specialist_nurse_referral_made = True
