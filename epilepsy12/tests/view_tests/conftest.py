"""
conftest for view_tests.

Every test in this subtree relies on the seeded E12 groups and users
(`seed_groups_fixture`, `seed_users_fixture`) being present, but most tests
do not declare them as explicit fixture dependencies - they look users up
by first_name (e.g. ``Epilepsy12User.objects.get(first_name=...)``) and
assume the rows already exist.

This autouse fixture makes the seed fixtures run for every test in this
directory without having to add them to every test signature. It is
session-scoped (matching the seed fixtures themselves) so the seed runs
once per pytest session (per xdist worker) - not once per test, which was
the 5x slowdown when this was function-scoped.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _seed_view_tests_data(seed_groups_fixture, seed_users_fixture):
    # The seed fixtures do all the work; this wrapper just ensures they are
    # requested once per session for every test in this subtree.
    yield
