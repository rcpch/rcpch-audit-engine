"""
conftest for view_tests.

Groups and the shared test users are seeded once per pytest session by the
autouse `seed_groups_and_users_fixture` in `epilepsy12/tests/conftest.py`.

Under pytest-xdist each worker is a separate pytest session with its *own*
test database (pytest-django suffixes the DB name with the worker id), so
each worker seeds its own DB before its first test. Tests in this subtree can
therefore look users up by `first_name` and `force_login` them without
requesting the seed fixtures explicitly.

Before this fixture existed, seeding only ran when a test explicitly
requested `seed_groups_fixture`/`seed_users_fixture`, so tests that read the
seeded users without requesting them passed or failed depending on whether
their worker happened to have run a seeder first — the source of the
intermittent CI failures in test_permissions_create.py /
test_permissions_delete.py (and latent in _update.py / _view.py).
"""
