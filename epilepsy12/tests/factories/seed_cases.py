"""
Seeds 2 E12 Cases in test db once per session. One user in GOSH. One user in different Trust (Addenbrooke's)
"""

# Standard imports
import pytest

# 3rd Party imports

# E12 Imports
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_lead_data,
)
from epilepsy12.models import (
    Organisation,
    Case
)
from .E12CaseFactory import E12CaseFactory
from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_LEAD,
)


@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_cases_fixture(django_db_setup, django_db_blocker):
    
    with django_db_blocker.unblock():
        
        # prevent repeat seed
        if not Case.objects.all().exists():

            GOSH = Organisation.objects.get(
                ODSCode="RP401",
                ParentOrganisation_ODSCode="RP4",
            )
            
            ADDENBROOKES = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )
            
            for organisation in [GOSH, ADDENBROOKES]:
                
                E12CaseFactory(
                    first_name=f"child_{organisation.OrganisationName}",
                    organisations__organisation = organisation,
                )
        
        


