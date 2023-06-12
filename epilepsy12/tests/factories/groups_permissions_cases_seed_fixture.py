import pytest
from django.core.management import call_command

from epilepsy12.management.commands.create_groups import groups_seeder
from epilepsy12.management.commands.seed import run_dummy_cases_seed, run_registrations

@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_groups_fixture(django_db_setup, django_db_blocker):
    """
    Fixture which runs once per session to seed groups 
    verbose=False
    """
    with django_db_blocker.unblock():

        groups_seeder(
            run_create_groups=True,
            verbose=False,
        )


@pytest.mark.django_db
@pytest.fixture(scope="session")
def cases_seeder(django_db_setup, django_db_blocker):
    """
    Fixture which runs once per session to seed cases
    verbose=False
    """
    with django_db_blocker.unblock():
        # run_dummy_cases_seed(
        #     verbose=False # don't print any stdout
        # )
        # run_registrations(
        #     verbose=False # don't print any stdout
        # )
        
        # UNCOMMENT ABOVE IF REQUIRING LOTS OF SEEDED REGISTERED CASES
        
        pass
