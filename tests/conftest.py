import pytest
from django.core.management import call_command

@pytest.mark.django_db
@pytest.fixture(scope='session')
def seeder(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        
        call_command('seed', '--mode=seed_dummy_cases')
        call_command('seed', '--mode=seed_registrations')
        call_command('seed', '--mode=seed_groups_and_permissions')