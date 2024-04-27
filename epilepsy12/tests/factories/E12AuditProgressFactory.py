"""
E12 Audit Progress Factory.
"""

# standard imports
import datetime

# third-party imports
import pytest
import factory

# rcpch imports
from epilepsy12.models import (
    AuditProgress,
)


class E12AuditProgressFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 AuditProgress"""

    class Meta:
        model = AuditProgress

    registration_complete = True
    first_paediatric_assessment_complete = True
    assessment_complete = True
    epilepsy_context_complete = True
    multiaxial_diagnosis_complete = True
    management_complete = True
    investigations_complete = True
    registration_total_expected_fields = 3
    registration_total_completed_fields = 0
    first_paediatric_assessment_total_expected_fields = 0
    first_paediatric_assessment_total_completed_fields = 0
    assessment_total_expected_fields = 0
    assessment_total_completed_fields = 0
    epilepsy_context_total_expected_fields = 0
    epilepsy_context_total_completed_fields = 0
    multiaxial_diagnosis_total_expected_fields = 0
    multiaxial_diagnosis_total_completed_fields = 0
    investigations_total_expected_fields = 0
    investigations_total_completed_fields = 0
    management_total_expected_fields = 0
    management_total_completed_fields = 0
