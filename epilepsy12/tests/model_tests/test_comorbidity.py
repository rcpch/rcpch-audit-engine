"""
Tests the Comorbidity model
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import Comorbidity, MultiaxialDiagnosis


@pytest.fixture
@pytest.mark.django_db
def multiaxial_diagnosis(db):
    return MultiaxialDiagnosis.objects.create(
        syndrome_present=False,
        epilepsy_cause_known=False,
        relevant_impairments_behavioural_educational=False,
        mental_health_screen=False,
        mental_health_issue_identified=False,
    )


@pytest.fixture
@pytest.mark.django_db
def comorbidity(db):
    return Comorbidity.objects.create(
        multiaxial_diagnosis=multiaxial_diagnosis,
    )


@pytest.mark.django_db
def test_comorbidity_diagnosis_date(comorbidity):
    assert comorbidity.comorbidity_diagnosis_date == None
