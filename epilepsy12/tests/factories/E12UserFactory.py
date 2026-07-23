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

from django.apps import apps

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

    email = factory.Faker("email")
    first_name = "Mandel"
    surname = "Brot"
    is_active = True
    is_superuser = False
    email_confirmed = True

    # add orgsanisation
    @factory.post_generation
    def employer_organisations(self, create, extracted, **kwargs):
        if not create:
            return

        #  get default organisation employer
        OrganisationEmployer = apps.get_model("epilepsy12", "OrganisationEmployer")
        default_organisation = Organisation.objects.filter(ods_code="RP401").first()
        if extracted:
            for org in extracted:

                OrganisationEmployer.objects.create(
                    epilepsy12_user=self,
                    employer_organisation=org,
                    is_primary=True,
                    is_active=True,
                )
        else:
            OrganisationEmployer.objects.create(
                epilepsy12_user=self,
                employer_organisation=default_organisation,
                is_primary=True,
                is_active=True,
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
