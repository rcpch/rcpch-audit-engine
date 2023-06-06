import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

# RCPCH IMPORTS
from epilepsy12.models import Organisation

@pytest.mark.examples
@pytest.mark.django_db
def test_how_to_use_access_edit_audit_form_factories(
    e12_case_factory
):
    
    # ALWAYS START WITH BUILDING A FRESH CASE as this builds all interconnected relations and dependencies
    case = e12_case_factory()
    
    print(f"{case.registration.firstpaediatricassessment}")
    print(f"{case.registration.epilepsycontext}")
    print(f"{case.registration.multiaxialdiagnosis}")
    print(f"{case.registration.assessment}")
    print(f"{case.registration.investigations}")
    print(f"{case.registration.management}")
    
    # override something
    case2 = e12_case_factory(
        registration__multiaxial_diagnosis__episode__epilepsy_or_nonepilepsy_status = 'NE',
        registration__assessment__no_referral_consultant_paediatrician = True # using the flag found in E12AssessmentFactory to override multiple values at once
    )
    
    from epilepsy12.models import Episode

    print(f"Episode after overriding: {Episode.objects.get(multiaxial_diagnosis=case2.registration.multiaxialdiagnosis)}")

@pytest.mark.examples
@pytest.mark.django_db
def test_create_e12user_should_pass():
    db = get_user_model()
    user = db.objects.create_user(
        email="testuser@epilepsy12.com",
        password="epilepsy12password",
        title=4,
        first_name="Henry",
        surname="Gastaut",
        role=1,
        organisation_employer=Organisation.objects.first(),
    )

    test_user = db.objects.first()
    assert db.objects.count() == 1
    assert all(
        [
            test_user.email == "testuser@epilepsy12.com",
            user.check_password("epilepsy12password"),
            test_user.first_name == "Henry",
            test_user.surname == "Gastaut",
        ]
    )


@pytest.mark.examples
@pytest.mark.django_db
def test_index_request_should_pass(client):
    url = reverse("index")
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/epilepsy12index.html"

    assert response.status_code == 200
    assert response.templates[0].name == EXPECTED_TEMPLATE_NAME


@pytest.mark.examples
@pytest.mark.django_db
def test_organisation_request_NOTAUTH_should_pass(client):
    """
    Non-authenticated user attempts accessing @login_required urls.
    """
    url = reverse("organisation_reports")
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/organisation.html"

    assert response.status_code != 200


