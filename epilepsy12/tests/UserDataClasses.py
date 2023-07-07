"""
Set up dataclasses for E12 User Test Fixtures
"""

# Standard Imports
from dataclasses import dataclass
from epilepsy12.common_view_functions import group_for_role

# RCPCH Imports
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_ADMINISTRATOR,
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)


@dataclass
class TestUser:
    role: int
    role_str: str 
    is_clinical_audit_team: bool = False
    is_active: bool = False
    is_staff: bool = False
    is_rcpch_audit_team_member: bool = False
    is_rcpch_staff: bool = False
    
    @property
    def group_name(self):
        return group_for_role(self.role)


test_user_audit_centre_administrator_data = TestUser(
    role=AUDIT_CENTRE_ADMINISTRATOR,
    is_active=False,
    is_staff=False,
    role_str="AUDIT_CENTRE_ADMINISTRATOR",
    is_rcpch_audit_team_member=False,
    is_rcpch_staff=False,
)

test_user_audit_centre_clinician_data = TestUser(
    role=AUDIT_CENTRE_CLINICIAN,
    role_str="AUDIT_CENTRE_CLINICIAN",
    is_active=False,
    is_staff=False,
    is_rcpch_audit_team_member=False,
    is_rcpch_staff=False,
)

test_user_audit_centre_lead_clinician_data = TestUser(
    role=AUDIT_CENTRE_LEAD_CLINICIAN,
    role_str="AUDIT_CENTRE_LEAD_CLINICIAN",
    is_active=False,
    is_staff=False,
    is_rcpch_audit_team_member=False,
    is_rcpch_staff=False,
)

test_user_clinicial_audit_team_data = TestUser(
    role=AUDIT_CENTRE_LEAD_CLINICIAN,
    role_str="CLINICAL_AUDIT_TEAM",
    is_active=False,
    is_staff=False,
    is_clinical_audit_team=True,
    is_rcpch_audit_team_member=True,
    is_rcpch_staff=False,
)

test_user_rcpch_audit_team_data = TestUser(
    role=RCPCH_AUDIT_TEAM,
    role_str="RCPCH_AUDIT_TEAM",
    is_active=False,
    is_staff=False,
    is_rcpch_audit_team_member=True,
    is_rcpch_staff=True,
)
