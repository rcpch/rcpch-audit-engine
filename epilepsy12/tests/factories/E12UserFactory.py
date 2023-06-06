"""Factory fn to create new E12 Users"""
# standard imports

# third-party imports
import factory
from django.contrib.auth import get_user_model

# rcpch imports
from epilepsy12.models import (
    Organisation,
)
from epilepsy12.constants import user_types


class E12UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()  # returns the Epilepsy12User object

    email = factory.Sequence(lambda n: f"e12_test_user_{n}@rcpch.com")
    password = "password"
    first_name = "Mandel"
    surname = "Brot"
    is_active = True
    is_staff = True
    is_rcpch_audit_team_member = True
    is_superuser = False
    role = user_types.AUDIT_CENTRE_LEAD_CLINICIAN
    email_confirmed = True
    organisation_employer = factory.LazyFunction(
        lambda: Organisation.objects.filter(ODSCode="RP401").first()
    )
