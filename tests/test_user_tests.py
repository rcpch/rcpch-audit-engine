import pytest

from django.contrib.auth import get_user_model
from epilepsy12.models import Organisation
from django.core.management import call_command

@pytest.mark.django_db
def test_epilepsy12user():
    print(f"{Organisation.objects.count() = }")
