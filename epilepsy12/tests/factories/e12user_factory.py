import pytest
from django.contrib.auth import get_user_model

from epilepsy12.constants import user_types
from epilepsy12.models import Organisation

@pytest.mark.django_db
@pytest.fixture()
def new_e12user_factory():
    def create_e12user(
        email: str,
        password: str = 'password',
        first_name: str = "Mandel",
        surname: str = "Brot",
        is_active: bool = True,
        is_staff: bool = True,
        is_rcpch_audit_team_member: bool = True,
        is_superuser: bool = False,
        role: int = user_types.AUDIT_CENTRE_LEAD_CLINICIAN,
        email_confirmed: bool = True,
        organisation_employer = Organisation.objects.get(ODSCode='RP401'),
    ):
        """
        Factory fn which creates a new e12 user for use in testing.
        
        Requires email.
        """

        e12user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            surname=surname,
            is_active=is_active,
            is_staff=is_staff,
            is_rcpch_audit_team_member=is_rcpch_audit_team_member,
            is_superuser=is_superuser,
            role=role,
            email_confirmed=email_confirmed,
            organisation_employer=organisation_employer
        )

        return e12user

    return create_e12user