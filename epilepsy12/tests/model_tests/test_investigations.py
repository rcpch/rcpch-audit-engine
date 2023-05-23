"""
Tests the Investigations model.

Tests:

    - 
"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    Investigations,
)


@pytest.mark.django_db
def test_registration_investigations_relation_success(
    e12Registration_2022,
):
    
    assert Investigations.objects.get(registration=e12Registration_2022)