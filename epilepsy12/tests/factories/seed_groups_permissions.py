import pytest

from epilepsy12.management.commands.create_groups import groups_seeder


@pytest.fixture(scope="session")
def seed_groups_fixture(django_db_setup, django_db_blocker):
    """
    Fixture which runs once per session to seed groups 
    verbose=False
    """
    with django_db_blocker.unblock():
        # groups_seeder is idempotent: it creates missing groups and adds
        # missing permissions to existing ones. Running it unconditionally
        # keeps reused test databases (--reuse-db) in step with any newly
        # added permissions.
        groups_seeder(verbose=False)

