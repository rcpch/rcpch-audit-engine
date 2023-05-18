"""
E12 Audit Progress Factory.
"""
# standard imports
import datetime

# third-party imports
import pytest
import factory
from django.contrib.auth import get_user_model

# rcpch imports
from epilepsy12.models import (
    AuditProgress,
)


class E12AuditProgressFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 AuditProgress"""

    class Meta:
        model = AuditProgress

    registration_complete = False
    first_paediatric_assessment_complete = False
    assessment_complete = False
    epilepsy_context_complete = False
    multiaxial_diagnosis_complete = False
    management_complete = False
    investigations_complete = False
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
