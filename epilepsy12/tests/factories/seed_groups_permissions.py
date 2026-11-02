import pytest

from epilepsy12.management.commands.create_groups import groups_seeder


@pytest.fixture(scope="session")
def seed_groups_fixture(django_db_setup, django_db_blocker):
    """
    Session-scoped: groups and permissions are additive and idempotent, and
    no test mutates them. Runs once per session (not per test) to avoid the
    ~20 ContentType lookups and per-permission get_or_create work in
    groups_seeder() running for every test that requests this fixture.

    Safe under xdist: under pytest-xdist each worker is a separate pytest
    session with its own test database (pytest-django suffixes the DB name
    with the worker id), so this runs once per worker. The autouse
    ``seed_groups_and_users_fixture`` in ``epilepsy12/tests/conftest.py``
    triggers it for every worker before its first test.
    """
    with django_db_blocker.unblock():
        # groups_seeder is idempotent: it creates missing groups and adds
        # missing permissions to existing ones. Running it unconditionally
        # keeps reused test databases (--reuse-db) in step with any newly
        # added permissions.
        groups_seeder(verbose=False)

