"""
conftest for view_tests.

Every test in this subtree relies on the seeded E12 groups and users
(`seed_groups_fixture`, `seed_users_fixture`) being present, but most tests
do not declare them as explicit fixture dependencies - they look users up
by first_name (e.g. ``Epilepsy12User.objects.get(first_name=...)``) and
assume the rows already exist.

Under a single-process run with session-scoped seed fixtures this worked
because the committed seed data was visible to every subsequent test. Under
pytest-xdist with function-scoped seed fixtures (required for cross-worker
transaction isolation), only tests that explicitly request the fixtures get
seeded data - the rest see an empty user table and fail with DoesNotExist.

This autouse fixture makes the seed fixtures run for every test in this
directory without having to add them to every test signature. It is
function-scoped (matching the seed fixtures themselves) so each test gets
its own seeded data inside its own transaction.
"""

import pytest


@pytest.fixture(scope="function", autouse=True)
def _seed_view_tests_data(seed_groups_fixture, seed_users_fixture):
    # The seed fixtures do all the work; this wrapper just ensures they are
    # requested for every test in this subtree.
    yield
