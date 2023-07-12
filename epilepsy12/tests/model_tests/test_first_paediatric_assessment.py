"""
Tests the FPA model.

Tests:

    - [ ] 
"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import FirstPaediatricAssessment

@pytest.mark.django_db
def test_fpa_valid_creation(
    e12_case_factory,
):
    case = e12_case_factory()

    assert FirstPaediatricAssessment.objects.filter(registration=case.registration).exists()
