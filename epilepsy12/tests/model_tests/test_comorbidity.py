"""
Tests the Comorbidity model
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import Comorbidity


@pytest.mark.django_db
def test_working_comorbidity(e12_case_factory):
    """Tests simply ensures a valid comorbidity is attached, with default values, to a case.
    """
    case = e12_case_factory()
      
    assert Comorbidity.objects.filter(multiaxial_diagnosis = case.registration.multiaxialdiagnosis)

    