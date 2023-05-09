import pytest

from django.contrib.auth import get_user_model
from epilepsy12.models import Organisation
from django.core.management import call_command

@pytest.mark.django_db
def test_create_epilepsy12user():
    user = get_user_model().objects.create(
        email='test@test.com',
        password='password',
        first_name='Test',
        role=1,
    )
    assert get_user_model().objects.count() == 1
    assert get_user_model().objects.first().email == 'test@test.com'
