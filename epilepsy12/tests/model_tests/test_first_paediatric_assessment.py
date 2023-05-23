"""
Tests the FPA model.

Tests:

    - [ ] 
"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports


@pytest.mark.django_db
def test_fpa_valid_creation(
    e12_first_paediatric_assessment_factory,
):
    fpa = e12_first_paediatric_assessment_factory()

    print(fpa)
    print(f"{fpa.registration}")
