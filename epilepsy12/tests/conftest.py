import pytest

from epilepsy12.tests.factories import (
    groups_cases_seeder, 
    new_e12user_factory
    )

"""
AVAILABLE USERS FOR TESTS
------------------------------------------
"""
@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH(new_e12user_factory):
    """
    Creates a single authenticated E12 User object instance for tests.
    """

    return new_e12user_factory(first_name = 'Norm', email='normal.user@test.com')

@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH_superuser(new_e12user_factory):
    """
    Creates a single authenticated SUPERUSER E12 User object instance for tests.
    """

    return new_e12user_factory(first_name = 'Zeus', email='superuser@test.com', is_superuser=True)
"""
------------------------------------------
"""