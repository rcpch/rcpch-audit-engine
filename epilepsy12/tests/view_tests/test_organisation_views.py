from datetime import date

import pytest

from dateutil.relativedelta import relativedelta
from django.urls import reverse

from ...constants.user_types import AUDIT_CENTRE_CLINICIAN
from ...models import Epilepsy12User
from ...tests.view_tests.permissions_tests.perm_tests_utils import twofactor_signin

@pytest.mark.django_db
def test_case_appears_in_trust_kpis(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that when a case is registered, it appears in the KPIs for the trust.
    """
    user = Epilepsy12User.objects.filter(
        employer_organisations__employer_organisation__ods_code="RP401",
        role=AUDIT_CENTRE_CLINICIAN,
    ).first()

    org = user.employer_organisations.first().employer_organisation

    client.force_login(user)
    twofactor_signin(client, test_user=user)

    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
        organisations__organisation=org
    )

    url = reverse("selected_trust_kpis", kwargs={
        "organisation_id": org.id,
        "access": "private"
    })

    response = client.get(url)

    assert response.status_code == 200

    
