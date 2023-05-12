import pytest 

from epilepsy12.models import (
    Keyword,
    )

@pytest.mark.django_db
def test_semiology_keyword():
    """
    Tests for the Semiology Keyword model.
    
    This should be seeded in migrations.
    """
    
    assert Keyword.objects.exists()
    
    
    