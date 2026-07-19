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
import uuid

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

    # The sequence restarts each pytest process, but session-scoped fixtures
    # (seed_users_fixture) commit users into the reused test DB (--reuse-db),
    # so plain sequenced emails collide across runs. Namespacing with a
    # per-process UUID fragment keeps every generated email unique while the
    # sequence keeps users distinct from each other within a run.
    _run_id = uuid.uuid4().hex[:8]
    email = factory.Sequence(lambda n: f"e12_test_user_{n}_{E12UserFactory._run_id}@nhs.net")
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
