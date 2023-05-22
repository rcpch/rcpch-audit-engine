"""
Tests the Multiaxial Diagnosis model
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    MultiaxialDiagnosis,
)


@pytest.mark.xfail
@pytest.mark.django_db
def test_working_e12MultiaxialDiagnosis_e12Case_relation(
    e12MultiaxialDiagnosis, e12Case
):
    # this assertion fails because the Case factory creates two differently-numbered Case objects
    assert e12MultiaxialDiagnosis.registration.case == e12Case
