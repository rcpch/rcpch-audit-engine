import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from epilepsy12.models import Organisation



@pytest.mark.django_db
def test_create_e12user_should_pass():
   
    from epilepsy12.management.commands.create_groups import create_groups
    
    create_groups()
    
    print(f"{Group.objects.all() = }")
    
    db = get_user_model()
    user = db.objects.create_user(
            email="testuser@epilepsy12.com",
            password="epilepsy12password",
            title=4,
            first_name="Henry",
            surname="Gastaut",
            role=1,
            organisation_employer = Organisation.objects.first()
        )
    print(f"{user=}")
    

    

@pytest.mark.django_db
def test_index_request_should_pass(client):
    url = reverse("index")
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/epilepsy12index.html"

    assert response.status_code == 200
    assert response.templates[0].name == EXPECTED_TEMPLATE_NAME


@pytest.mark.django_db
def test_organisation_request_NOTAUTH_should_pass(client):
    """
    Non-authenticated user attempts accessing @login_required urls.
    """
    url = reverse("organisation_reports")
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/organisation.html"

    assert response.status_code != 200



