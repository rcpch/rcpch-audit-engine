!!!note "Conservative Database Access"
    By default, Pytest does *not* allow database access in its tests.

    If you require a test to access the database, mark it with the `@pytest.mark.django_db` decorator.

    Alternatively, you can feed it in as a fixture. However, we only use marks for consistency.
