"""
Tests the Audit Progress model
"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import AuditProgress, Registration
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    update_audit_progress,
)

@pytest.mark.django_db
def test_audit_progress_creation(
    e12_case_factory,
):
    """Creates an audit progress with audit values filled using default values.
    """
    case = e12_case_factory().registration.audit_progress
    
    assert case.registration.audit_progress

# @pytest.mark.django_db
# def test_audit_progress_creation(e12Registration_2022):
#     """
#     Tests that an empty AuditProgress object can be created and has correct initial values
#     """
#     # Create an AuditProgress object
#     audit_progress = AuditProgress.objects.create()

#     # Check that the AuditProgress has the correct initial values
#     assert audit_progress.registration_complete is False
#     assert audit_progress.registration_total_expected_fields == 0
#     assert audit_progress.registration_total_completed_fields == 0
#     assert audit_progress.audit_complete is False

#     # Add the Registration object to the AuditProgress object
#     # Update the AuditProgress object
#     update_audit_progress(e12Registration_2022)

#     assert e12Registration_2022.audit_progress.registration_complete is False
#     assert e12Registration_2022.audit_progress.registration_total_expected_fields == 3


# first_paediatric_assessment_complete
# first_paediatric_assessment_total_expected_fields
# first_paediatric_assessment_total_completed_fields

# assessment_complete
# assessment_total_expected_fields
# assessment_total_completed_fields

# epilepsy_context_complete
# epilepsy_context_total_expected_fields
# epilepsy_context_total_completed_fields

# multiaxial_diagnosis_complete
# multiaxial_diagnosis_total_expected_fields
# multiaxial_diagnosis_total_completed_fields

# investigations_complete
# investigations_total_expected_fields
# investigations_total_completed_fields

# management_complete
# management_total_expected_fields
# management_total_completed_fields

# total_completed_fields
# total_expected_fields
