"""
Registration


First Paediatric Assessment

Epilepsy Context

Multiaxial
"""

# python imports
import pytest

# django imports
from django.urls import reverse

# E12 imports
# E12 imports
from epilepsy12.models import Epilepsy12User, Organisation, Case


@pytest.mark.skip(reason="Unfinished test.")
@pytest.mark.django_db
def test_completed_fields_success(
    client,
):
    """
    Simulating numerator in form calculation from numbers of scored fields in a given model is correct
    """
