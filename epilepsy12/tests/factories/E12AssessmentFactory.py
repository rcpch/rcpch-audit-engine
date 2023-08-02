"""Factory fn to create new E12 Assessments, related to a created Registration.
"""
# standard imports
from datetime import date
from dateutil.relativedelta import relativedelta

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

    Effect on related Site model:
        - if relevant referral is True ON CREATION, the relevant Site attribute related to that referral will be True e.g. if `consultant_paediatrician_referral_made=True`, then Site.site_is_general_paediatric_centre will be set to True. These Site attributes are FALSE by default.

    Flags:
        - `pass_paediatrician_with_expertise_in_epilepsies` - if True, sets plausible answers so score passes this KPI
        - `fail_paediatrician_with_expertise_in_epilepsies` - if True, sets plausible answers so score fails this KPI
    """

    class Meta:
        model = Assessment
        skip_postgeneration_save=True

    # Once Registration instance made, it will attach to this instance
    registration = None

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

    class Params:
        
        # KPI 1
        pass_paediatrician_with_expertise_in_epilepsies = factory.Trait(
            consultant_paediatrician_referral_made=True,
            consultant_paediatrician_referral_date=date(2023, 1, 1),
            consultant_paediatrician_input_date=date(2023, 1, 2),
        )

        fail_paediatrician_with_expertise_in_epilepsies = factory.Trait(
            consultant_paediatrician_referral_made=True,
            consultant_paediatrician_referral_date=date(2023, 1, 1),
            consultant_paediatrician_input_date=date(2023, 2, 1),
            paediatric_neurologist_referral_made=True,
            paediatric_neurologist_referral_date=date(2023, 1, 1),
            paediatric_neurologist_input_date=date(2023, 2, 1),
        )

        # KPI 2
        pass_epilepsy_specialist_nurse = factory.Trait(
            epilepsy_specialist_nurse_referral_made=True,
            epilepsy_specialist_nurse_referral_date=factory.LazyAttribute(
                lambda o: o.registration.registration_date + relativedelta(days=5)
            ),
            epilepsy_specialist_nurse_input_date=factory.LazyAttribute(
                lambda o: o.epilepsy_specialist_nurse_referral_date + relativedelta(days=5)
            ),
        )

        fail_epilepsy_specialist_nurse = factory.Trait(
            epilepsy_specialist_nurse_referral_made=False,
        )
        
        # KPI 3 and 3b
        pass_tertiary_input_AND_epilepsy_surgery_referral = factory.Trait(
            childrens_epilepsy_surgical_service_referral_criteria_met = True,
            paediatric_neurologist_referral_made = True,
            childrens_epilepsy_surgical_service_referral_made = True,
        )

        fail_tertiary_input_AND_epilepsy_surgery_referral = factory.Trait(
            childrens_epilepsy_surgical_service_referral_criteria_met = True,
            paediatric_neurologist_referral_made = False,
            childrens_epilepsy_surgical_service_referral_made = False,
        )
        
        ineligible_tertiary_input_AND_epilepsy_surgery_referral = factory.Trait(
            childrens_epilepsy_surgical_service_referral_criteria_met = False,
        )
        
