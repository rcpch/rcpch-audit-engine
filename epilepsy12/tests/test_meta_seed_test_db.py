import pytest 

from django.contrib.auth.models import Group

from epilepsy12.models import Epilepsy12User, Case

@pytest.mark.django_db
def test__seed_test_db(seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,):
    
    assert Group.objects.all().exists()
    assert Case.objects.all().exists()
    assert Epilepsy12User.objects.all().exists()