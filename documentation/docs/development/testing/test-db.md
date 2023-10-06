---
reviewers: Dr Anchit Chandran
---

The test database used by Pytest will be automatically set up the first time `pytest` is run. The test database mirrors E12's database, applying the same migrations and seeding functions, including:

- Seeding Cases
- Seeding Groups & Permissions

This initial setup is scoped to once per session and persists between subsequent test runs. In practice, this means the first time you run `pytest`, it may take a few minutes to set up, but subsequent runs should be much quicker as the pre-seeded database will be used.

--8<--
docs/_assets/_snippets/pytest-db-access.md
--8<--