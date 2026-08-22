"""
conftest for view_tests.

The seed fixtures (`seed_groups_fixture`, `seed_users_fixture`) are
session-scoped and commit their rows via `django_db_blocker.unblock()`.
Committed session data is visible to every test in this subtree (and every
xdist worker's own connection), so tests that look users up by `first_name`
and `force_login` them work without an autouse wrapper.

Tests that need the seed data should request the fixtures explicitly in their
signature (`seed_groups_fixture, seed_users_fixture`); the fixtures run once
per session so there is no per-test cost.
"""
