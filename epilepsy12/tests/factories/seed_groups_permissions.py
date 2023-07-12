import pytest

from django.contrib.auth.models import Group

from epilepsy12.management.commands.create_groups import groups_seeder

@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_groups_fixture(django_db_setup, django_db_blocker):
    """
    Fixture which runs once per session to seed groups 
    verbose=False
    """
    with django_db_blocker.unblock():

        if not Group.objects.all().exists():
            groups_seeder(
                run_create_groups=True,
                verbose=False,
            )
        else:
            print('Groups already seeded. Skipping')

