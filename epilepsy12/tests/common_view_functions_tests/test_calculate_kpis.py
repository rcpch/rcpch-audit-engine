"""
Tests for the calculate_kpi function.
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis

@pytest.mark.django_db
def test_calculate_kpi_function(
    e12_case_factory,
):
    """Creates an audit progress with fields filled using default values.
    """
    case = e12_case_factory()
    
    calculate_kpis(case.registration)
    
    print(case.registration.kpi)
    for attr, val in vars(case.registration.kpi).items():
        print(f"{attr} = {val}")