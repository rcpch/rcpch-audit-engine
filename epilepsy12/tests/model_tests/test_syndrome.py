import pytest 

from epilepsy12.models import (
    Syndrome,
    SyndromeEntity,
    MultiaxialDiagnosis,
    )

@pytest.mark.django_db
def test_syndrome():
    """
    Tests for the Syndrome model.
    
    This should be seeded in migrations.
    """
    
    # verify syndromes (and their dependent foreign keys) exist
    assert all([
        SyndromeEntity.objects.exists(),
        MultiaxialDiagnosis.objects.exists(),
        Syndrome.objects.exists(),
        ])
    
    
    