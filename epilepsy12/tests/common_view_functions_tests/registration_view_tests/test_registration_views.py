# python imports
import pytest
import random
from datetime import date

# django imports
from django.urls import reverse

# 3rd party imports
from dateutil.relativedelta import relativedelta

# E12 imports
from epilepsy12.models import Organisation, Epilepsy12User, Site, KPI

from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.tests.UserDataClasses import (
    test_user_rcpch_audit_team_data,
)


@pytest.mark.django_db
def test_transfer_centre(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Transfer lead centre to another centre

    This tests that the Site model and the KPI organisation instances are updated
    when the lead centre is transferred to another centre.
    """

    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )

    # Delete any existing Site instances associated with the Case
    Site.objects.filter(case=case).delete()

    # Create the Site instance and set the field - GOSH is the primary site of care and will make a transfer request to KCH
    lead_site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=False,
        transfer_origin_organisation=None,
        transfer_request_date=None,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=False,
        site_is_childrens_epilepsy_surgery_centre=False,
        site_is_paediatric_neurology_centre=False,
    )
    case.organisations.add(GOSH)
    case.registration.kpi.organisation = GOSH
    case.registration.kpi.save()

    # Login the user making the transfer request with the correct permissions
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )
    test_user.set_organisation_employer(organisation_employer=GOSH, is_primary=True)

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # Transfer the lead centre to KCH
    url = reverse(
        "update_lead_site",
        kwargs={
            "registration_id": case.registration.pk,
            "site_id": lead_site.pk,
            "update": "transfer",
        },
    )

    response = client.post(
        url,
        data={"transfer_lead_site": KCH.pk},  # KCH
        headers={"Hx-Trigger-Name": url, "Hx-Request": "true"},
    )

    assert response.status_code == 200

    # Check that the Site instance has been updated
    lead_site = Site.objects.get(
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        case=case,
    )

    # refresh KPI instance
    kpi = KPI.objects.get(pk=case.registration.kpi.pk)

    assert (
        lead_site.organisation == KCH
    ), f"The Site instance has not been updated to {KCH}"
    assert (
        lead_site.site_is_primary_centre_of_epilepsy_care == True
    ), "The Site instance primary centre status has not been updated to True"
    assert (
        lead_site.site_is_actively_involved_in_epilepsy_care == True
    ), "The Site instance active involvement status has not been updated to True"
    assert (
        kpi.organisation == KCH
    ), f"The KPI organisation instance has not been updated to {KCH}"
