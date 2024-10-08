import pytest

from django.urls import reverse

from epilepsy12.models import (
    Organisation,
    Epilepsy12User,
    Trust,
    LocalHealthBoard,
    OrganisationalAuditSubmission,
    OrganisationalAuditSubmissionPeriod,
)
from epilepsy12.constants import (
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_ADMINISTRATOR,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.parametrize("group", ["trust", "local_health_board"])
def test_anonymous_user_cannot_access_organisational_audit(client, group):
    response = client.get(reverse(f"organisational_audit_{group}", kwargs={f"id": 1}))

    assert response.status_code == 302
    assert response.headers["Location"] == "/account/login/"


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(AUDIT_CENTRE_CLINICIAN, id="clinican"),
        pytest.param(AUDIT_CENTRE_ADMINISTRATOR, id="administrator"),
    ],
)
@pytest.mark.django_db
def test_non_leads_cannot_access_organisational_audit_for_their_trust(
    client, seed_groups_fixture, seed_users_fixture, role
):
    gosh_org = Organisation.objects.get(ods_code="RP401")
    gosh_trust = Trust.objects.get(ods_code="RP4")

    gosh_user = Epilepsy12User.objects.get(
        role=role, organisation_employer__ods_code="RP401"
    )

    client.force_login(gosh_user)
    twofactor_signin(client, gosh_user)

    response = client.get(
        reverse("organisational_audit_trust", kwargs={"id": gosh_trust.id})
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(AUDIT_CENTRE_CLINICIAN, id="clinican"),
        pytest.param(AUDIT_CENTRE_ADMINISTRATOR, id="administrator"),
    ],
)
@pytest.mark.django_db
def test_non_leads_cannot_access_organisational_audit_for_their_local_health_board(
    client, seed_groups_fixture, seed_users_fixture, role
):
    noahs_ark_org = Organisation.objects.get(ods_code="7A4H1")
    noahs_ark_user = Epilepsy12User.objects.get(
        role=role, organisation_employer__ods_code="7A4H1"
    )

    noahs_ark_local_health_board = LocalHealthBoard.objects.get(ods_code="7A4")

    client.force_login(noahs_ark_user)
    twofactor_signin(client, noahs_ark_user)

    response = client.get(
        reverse(
            "organisational_audit_local_health_board",
            kwargs={"id": noahs_ark_local_health_board.id},
        )
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_lead_clinician_can_access_organisational_audit_for_their_trust(
    client, seed_groups_fixture, seed_users_fixture
):

    gosh_org = Organisation.objects.get(ods_code="RP401")
    gosh_trust = Trust.objects.get(ods_code="RP4")

    # Create an OrganisationalAuditSubmissionPeriod instance
    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2021, is_open=True
    )
    organisational_audit_submission = OrganisationalAuditSubmission.objects.create(
        submission_period=submission_period,
        trust=gosh_trust,
    )

    gosh_user = Epilepsy12User.objects.filter(
        role=AUDIT_CENTRE_LEAD_CLINICIAN, organisation_employer__ods_code="RP401"
    ).first()

    client.force_login(gosh_user)
    twofactor_signin(client, gosh_user)

    response = client.get(
        reverse("organisational_audit_trust", kwargs={"id": gosh_trust.id})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_lead_clinician_can_access_organisational_audit_for_their_local_health_board(
    client, seed_groups_fixture, seed_users_fixture
):
    noahs_ark_org = Organisation.objects.get(ods_code="7A4H1")
    noahs_ark_user = Epilepsy12User.objects.filter(
        role=AUDIT_CENTRE_LEAD_CLINICIAN, organisation_employer__ods_code="7A4H1"
    ).first()

    noahs_ark_local_health_board = LocalHealthBoard.objects.get(ods_code="7A4")

    # Create an OrganisationalAuditSubmissionPeriod instance
    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2021, is_open=True
    )
    organisational_audit_submission = OrganisationalAuditSubmission.objects.create(
        submission_period=submission_period,
        local_health_board=noahs_ark_local_health_board,
    )

    client.force_login(noahs_ark_user)
    twofactor_signin(client, noahs_ark_user)

    response = client.get(
        reverse(
            "organisational_audit_local_health_board",
            kwargs={"id": noahs_ark_local_health_board.id},
        )
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(AUDIT_CENTRE_CLINICIAN, id="clinican"),
        pytest.param(AUDIT_CENTRE_ADMINISTRATOR, id="administrator"),
        pytest.param(AUDIT_CENTRE_LEAD_CLINICIAN, id="lead_clinician"),
    ],
)
@pytest.mark.django_db
def test_users_cannot_access_organisational_audit_for_a_trust_that_isnt_theirs(
    client, seed_groups_fixture, seed_users_fixture, role
):
    gosh_org = Organisation.objects.get(ods_code="RP401")
    gosh_user = Epilepsy12User.objects.filter(
        role=role, organisation_employer__ods_code="RP401"
    ).first()

    client.force_login(gosh_user)
    twofactor_signin(client, gosh_user)

    kings_org = Trust.objects.get(ods_code="RJZ")

    response = client.get(
        reverse("organisational_audit_trust", kwargs={"id": kings_org.id})
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(AUDIT_CENTRE_CLINICIAN, id="clinican"),
        pytest.param(AUDIT_CENTRE_ADMINISTRATOR, id="administrator"),
        pytest.param(AUDIT_CENTRE_LEAD_CLINICIAN, id="lead_clinician"),
    ],
)
@pytest.mark.django_db
def test_users_cannot_access_organisational_audit_for_a_local_health_board_that_isnt_theirs(
    client, seed_groups_fixture, seed_users_fixture, role
):
    gosh_org = Organisation.objects.get(ods_code="RP401")
    gosh_user = Epilepsy12User.objects.filter(
        role=role, organisation_employer__ods_code="RP401"
    ).first()

    client.force_login(gosh_user)
    twofactor_signin(client, gosh_user)

    noahs_ark_local_health_board = LocalHealthBoard.objects.get(ods_code="7A4")

    response = client.get(
        reverse(
            "organisational_audit_local_health_board",
            kwargs={"id": noahs_ark_local_health_board.id},
        )
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_rcpch_audit_team_can_access_all_organisational_audits(
    client, seed_groups_fixture, seed_users_fixture
):
    rcpch_user = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    client.force_login(rcpch_user)
    twofactor_signin(client, rcpch_user)

    gosh_trust = Trust.objects.get(ods_code="RP4")
    noahs_ark_local_health_board = LocalHealthBoard.objects.get(ods_code="7A4")

    # Create an OrganisationalAuditSubmissionPeriod instance
    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2021, is_open=True
    )
    english_organisational_audit_submission = (
        OrganisationalAuditSubmission.objects.create(
            submission_period=submission_period,
            trust=gosh_trust,
        )
    )
    welsh_organisational_audit_submission = (
        OrganisationalAuditSubmission.objects.create(
            submission_period=submission_period,
            local_health_board=noahs_ark_local_health_board,
        )
    )

    response = client.get(
        reverse("organisational_audit_trust", kwargs={"id": gosh_trust.id})
    )
    assert response.status_code == 200

    response = client.get(
        reverse(
            "organisational_audit_local_health_board",
            kwargs={"id": noahs_ark_local_health_board.id},
        )
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_organisational_audit_for_trust_that_doesnt_exist(
    client, seed_groups_fixture, seed_users_fixture
):
    rcpch_user = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    client.force_login(rcpch_user)
    twofactor_signin(client, rcpch_user)

    response = client.get(reverse("organisational_audit_trust", kwargs={"id": 0}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_organisational_audit_for_local_health_board_that_doesnt_exist(
    client, seed_groups_fixture, seed_users_fixture
):
    rcpch_user = Epilepsy12User.objects.filter(is_rcpch_audit_team_member=True).first()

    client.force_login(rcpch_user)
    twofactor_signin(client, rcpch_user)

    response = client.get(
        reverse("organisational_audit_local_health_board", kwargs={"id": 0})
    )
    assert response.status_code == 404
