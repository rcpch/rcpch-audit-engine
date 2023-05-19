"""
Tests the Comorbidity model
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import Comorbidity, ComorbidityEntity, MultiaxialDiagnosis


@pytest.fixture
def comorbidity_entity(db):
    # picks the first comorbidity entity from the database
    return ComorbidityEntity.objects.get(pk=1)


@pytest.fixture
def comorbidity(db, e12MultiaxialDiagnosis_2022, comorbidity_entity):
    return Comorbidity.objects.create(
        multiaxial_diagnosis=e12MultiaxialDiagnosis_2022,
        comorbidityentity=comorbidity_entity,
    )


def test_comorbidity_diagnosis_date(db, comorbidity):
    assert comorbidity.comorbidity_diagnosis_date == None
