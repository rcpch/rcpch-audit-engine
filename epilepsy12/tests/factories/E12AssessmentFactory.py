"""Factory fn to create new E12 Assessments, related to a created Registration.
"""
# standard imports

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

    """

    class Meta:
        model = Assessment

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
