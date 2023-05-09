import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_index_request(client):
    url = reverse('index')
    response = client.get(url)
    EXPECTED_TEMPLATE_NAME = 'epilepsy12/epilepsy12index.html'
    
    assert response.status_code == 200
    assert response.templates[0].name == EXPECTED_TEMPLATE_NAME
    