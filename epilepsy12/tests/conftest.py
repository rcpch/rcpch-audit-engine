import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model

from epilepsy12.models import (
    VisitActivity,
    Organisation,
    )

@pytest.mark.django_db
@pytest.fixture(scope='session')
def seeder(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        
        call_command('seed', '--mode=seed_dummy_cases')
        call_command('seed', '--mode=seed_registrations')
        call_command('seed', '--mode=seed_groups_and_permissions')

@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH():
    """
    Creates a single minimal authenticated E12 User object instance for tests, scoped to session.
    Organisation = Great Ormond Street Hospital
    """
    
    e12_user = get_user_model().objects.create(
            email="testuser@epilepsy12.com",
            first_name="Marcus",
            surname="Aurelius",
            role=1,
            organisation_employer = Organisation.objects.get(ODSCode='RP401')
        )
    
    e12_user.set_password('password')
    
    e12_user.save()
    
    return e12_user