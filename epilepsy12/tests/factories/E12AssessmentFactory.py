"""Factory fn to create new E12 Assessments, related to a created Registration.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Assessment,
    Site,
)


class E12AssessmentFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Registration.

    This Factory is generated AFTER a Registration is created.

    Default:
        - referrals for consultant paediatrician, neurologist, epilepsy surgical service, specialist nurse all made 28 days after registration date
            - input for all services comes 5 weeks after referra;

    Effect on related Site model:
        - if relevant referral is True, the relevant Site attribute related to that referral will be True e.g. if `consultant_paediatrician_referral_made=True`, then Site.site_is_general_paediatric_centre will be set to True. These Site attributes are FALSE by default.

    Flags:
        - `no_referral_consultant_paediatrician` - if True, will set referral_made to False, and relevant dates to None
        - `no_referral_paediatric_neurologist` - if True, will set referral_made to False, and relevant dates to None
        - `no_referral_childrens_epilepsy_surgical_service` - if True, will set referral_made to False, and relevant dates to None
        - `no_referral_epilepsy_specialist_nurse` - if True, will set referral_made to False, and relevant dates to None
    """

    class Meta:
        model = Assessment

    # Once Registration instance made, it will attach to this instance
    registration = None

    childrens_epilepsy_surgical_service_referral_criteria_met = True

    consultant_paediatrician_referral_made = True
    consultant_paediatrician_referral_date = factory.lazy_attribute(
        lambda assessment: assessment.registration.registration_date
        + timedelta(days=28)
    )
    consultant_paediatrician_input_date = factory.lazy_attribute(
        lambda assessment: assessment.consultant_paediatrician_referral_date
        + timedelta(days=5)
    )

    paediatric_neurologist_referral_made = True
    paediatric_neurologist_referral_date = factory.lazy_attribute(
        lambda assessment: assessment.registration.registration_date
        + timedelta(days=28)
    )
    paediatric_neurologist_input_date = factory.lazy_attribute(
        lambda assessment: assessment.paediatric_neurologist_referral_date
        + timedelta(weeks=5)
    )

    childrens_epilepsy_surgical_service_referral_made = True
    childrens_epilepsy_surgical_service_referral_date = factory.lazy_attribute(
        lambda assessment: assessment.registration.registration_date
        + timedelta(days=28)
    )
    childrens_epilepsy_surgical_service_input_date = factory.lazy_attribute(
        lambda assessment: assessment.childrens_epilepsy_surgical_service_referral_date
        + timedelta(weeks=5)
    )

    epilepsy_specialist_nurse_referral_made = True
    epilepsy_specialist_nurse_referral_date = factory.lazy_attribute(
        lambda assessment: assessment.registration.registration_date
        + timedelta(days=28)
    )
    epilepsy_specialist_nurse_input_date = factory.lazy_attribute(
        lambda assessment: assessment.epilepsy_specialist_nurse_referral_date
        + timedelta(weeks=5)
    )

    class Params:
        no_referral_consultant_paediatrician = factory.Trait(
            consultant_paediatrician_referral_made=False,
            consultant_paediatrician_referral_date=None,
            consultant_paediatrician_input_date=None,
        )
        no_referral_paediatric_neurologist = factory.Trait(
            paediatric_neurologist_referral_made=False,
            paediatric_neurologist_referral_date=None,
            paediatric_neurologist_input_date=None,
        )
        no_referral_childrens_epilepsy_surgical_service = factory.Trait(
            childrens_epilepsy_surgical_service_referral_made=False,
            childrens_epilepsy_surgical_service_referral_date=None,
            childrens_epilepsy_surgical_service_input_date=None,
        )
        no_referral_epilepsy_specialist_nurse = factory.Trait(
            epilepsy_specialist_nurse_referral_made=False,
            epilepsy_specialist_nurse_referral_date=None,
            epilepsy_specialist_nurse_input_date=None,
        )

    # once assessment filled, will set corresponding Site attributes depending on these values
    @factory.post_generation
    def set_site_attribute(self, create, extracted, **kwargs):
        if create:
            site = Site.objects.get(case=self.registration.case)

            if self.consultant_paediatrician_referral_made:
                site.site_is_general_paediatric_centre = True
            if self.paediatric_neurologist_referral_made:
                site.site_is_paediatric_neurology_centre = True
            if self.childrens_epilepsy_surgical_service_referral_made:
                site.site_is_childrens_epilepsy_surgery_centre = True

            site.save()
