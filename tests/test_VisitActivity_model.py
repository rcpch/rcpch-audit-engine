import time

import pytest 
from django.urls import reverse
from django.contrib.auth import login, get_user_model

from epilepsy12.models import (
    VisitActivity,
    Organisation,
    )

@pytest.mark.django_db
def test_visitActivity(e12User_GOSH, client):
    """
    Test that visit activity logging works, using visitActivity fixture
    """
    
    client.force_login(e12User_GOSH)

    visit_activity = VisitActivity.objects.all()
    
    time.sleep(1)
    
    client.force_login(e12User_GOSH)
    
    assert len(visit_activity) == 2
    assert visit_activity[1].activity_datetime > visit_activity[0].activity_datetime

@pytest.mark.django_db
def test_organisation_view_correct_visit_activity_logging(e12User_GOSH, client):
    """
    Test that the message showing on organisation view after user logs is correct.
    """
    
    
    