"""
Set up dataclasses for E12 User Test Fixtures
"""

# Standard Imports
from dataclasses import dataclass

# RCPCH Imports
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_ADMINISTRATOR,
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_LEAD,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)

@dataclass
class TestUser:
    role: int
    role_str: str
    group_name: str

test_user_audit_centre_administrator_data = TestUser(
    role=AUDIT_CENTRE_ADMINISTRATOR,
    role_str="AUDIT_CENTRE_ADMINISTRATOR",
    group_name=TRUST_AUDIT_TEAM_EDIT_ACCESS,
)

test_user_audit_centre_clinician_data = TestUser(
    role=AUDIT_CENTRE_CLINICIAN,
    role_str="AUDIT_CENTRE_CLINICIAN",
    group_name=TRUST_AUDIT_TEAM_EDIT_ACCESS,
)

test_user_audit_centre_lead_clinician_data = TestUser(
    role=AUDIT_CENTRE_LEAD_CLINICIAN,
    role_str="AUDIT_CENTRE_LEAD_CLINICIAN",
    group_name=TRUST_AUDIT_TEAM_FULL_ACCESS,
)

test_user_rcpch_audit_lead_data = TestUser(
    role=RCPCH_AUDIT_LEAD,
    role_str="RCPCH_AUDIT_LEAD",
    group_name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)