import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_index_request_should_pass(client):
    url = reverse('index')
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/epilepsy12index.html"
    
    assert response.status_code == 200
    assert response.templates[0].name == EXPECTED_TEMPLATE_NAME


@pytest.mark.django_db
def test_organisation_request_NOTAUTH_should_pass(client):
    """
    Non-authenticated user attempts accessing @login_required urls.
    """
    url = reverse('organisation_reports')
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = "epilepsy12/organisation.html"
    
    assert response.status_code != 200
    