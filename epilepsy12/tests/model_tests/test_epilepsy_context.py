"""
Tests the Epilepsy Context model.

Tests:

    - 
"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    Case
)

@pytest.mark.django_db
def test_epilepsy_context_valid_creation(
    e12_epilepsy_context_factory,
):
    
    ec = e12_epilepsy_context_factory()
    
    assert ec.registration.case == Case.objects.first()
