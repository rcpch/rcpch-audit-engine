# 3rd PARTY IMPORTS
from django.contrib.auth.models import Group
import pytest

# RCPCH IMPORTS
from epilepsy12.models import Case

@pytest.mark.seed
@pytest.mark.django_db
def test_groups__cases_seeded_and_exist(groups_cases_seeder):
    """
    Ensures the groups and cases are seeded for tests.
    """
    
    groups = Group.objects.count()
    cases = Case.objects.count()

    assert groups > 0
    assert cases > 0