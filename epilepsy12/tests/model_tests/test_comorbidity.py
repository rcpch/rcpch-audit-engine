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
def multiaxial_diagnosis(db, e12Registration_2022):
    return MultiaxialDiagnosis.objects.create(
        syndrome_present=False,
        epilepsy_cause_known=False,
        relevant_impairments_behavioural_educational=False,
        mental_health_screen=False,
        mental_health_issue_identified=False,
        registration=e12Registration_2022,
    )


@pytest.fixture
def comorbidity(db, multiaxial_diagnosis, comorbidity_entity):
    return Comorbidity.objects.create(
        multiaxial_diagnosis=multiaxial_diagnosis,
        comorbidityentity=comorbidity_entity,
    )


def test_comorbidity_diagnosis_date(db, comorbidity):
    assert comorbidity.comorbidity_diagnosis_date == None
