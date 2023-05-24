"""Factory fn to create new E12 Cases"""
# standard imports
import datetime

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Case
from .E12SiteFactory import E12SiteFactory
from .E12RegistrationFactory import E12RegistrationFactory
from epilepsy12.constants import VALID_NHS_NUMS


class E12CaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Case

    # TODO - once Case.nhs_number has appropriate validation + cleaning, won't need to strip spaces here
    nhs_number = factory.Sequence(lambda n: VALID_NHS_NUMS[n].replace(" ", ""))
    first_name = "Thomas"
    surname = factory.Sequence(lambda n: f"Anderson-{n}")  # Anderson-1, Anderson-2, ...
    sex = 1
    date_of_birth = datetime.date(2021, 9, 2)
    ethnicity = "A"
    locked = False

    @factory.post_generation
    def organisations(self, create, extracted, **kwargs):
        if not create:
            # factory NOT called with .create() method
            return

        E12SiteFactory.create(case=self)
    
    # reverse dependencies
    registration = factory.RelatedFactory(
        E12RegistrationFactory,
        factory_related_name="case",
    )
