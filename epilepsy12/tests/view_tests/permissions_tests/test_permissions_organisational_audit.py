import pytest

from django.urls import reverse

@pytest.mark.parametrize("group", [
    pytest.param("trust", id = "Trust"),
    pytest.param("health_board", id = "Health Board")
])
def test_anonymous_user_cannot_access_organisational_audit(client, group):
    response = client.get(reverse(f"organisational_audit_{group}", kwargs={ "id": 1 }))

    assert(response.status_code == 302)
    assert(response.headers["Location"] == "/account/login/")


@pytest.mark.parametrize("group,role", [
    ("trust", "clinician"),
    ("trust", "administrator"),
    ("health_board", "clinician"),
    ("health_board", "administrator")
])
def test_non_leads_cannot_access_organisational_audit_for_their_group(client, seed_groups_fixture, seed_users_fixture, group, role):
    # user =  

    raise Exception('not implemented yet')


@pytest.mark.parametrize("group,role", [
    ("trust", "clinician"),
    ("trust", "administrator"),
    ("health_board", "clinician"),
    ("health_board", "administrator")
])
def test_non_leads_cannot_access_organisational_audit_for_another_group(seed_groups_fixture, seed_users_fixture, group, role):
    # user =  

    raise Exception('not implemented yet')


def test_lead_clinician_can_access_organisational_audit_for_their_trust():
    raise Exception('not implemented yet')


def test_lead_clinician_cannot_access_organisational_audit_for_another_trust():
    raise Exception('not implemented yet')


def test_lead_clinician_cannot_access_organisational_audit_for_another_health_board():
    raise Exception('not implemented yet')


def test_rcpch_audit_team_can_access_organisational_audit_for_any_trust():
    raise Exception('not implemented yet')


def test_rcpch_audit_team_can_access_organisational_audit_for_any_health_board():
    raise Exception('not implemented yet')