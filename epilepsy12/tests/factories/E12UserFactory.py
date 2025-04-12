"""Factory fn to create new E12 Users.

Note default values include:
    - organisation = GOSH
    - is_superuser = False

The following parameters must be specified:

    - is_staff
    - is_rcpch_audit_team_member
    - role 

"""

# standard imports

# third-party imports
import factory
from epilepsy12.models import Epilepsy12User

# rcpch imports
from epilepsy12.models import (
    Organisation,
)


class E12UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Epilepsy12User  # returns the Epilepsy12User object
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"e12_test_user_{n}@nhs.net")
    first_name = "Mandel"
    surname = "Brot"
    is_active = True
    is_superuser = False
    email_confirmed = True
    organisation_employer = factory.LazyFunction(
        lambda: Organisation.objects.filter(ods_code="RP401", active=True).first()
    )

    # Add Groups
    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        # hook into post gen hook to set pass
        self.set_password("pw")

        if extracted:
            for group in extracted:
                self.groups.add(group)

            self.save()
