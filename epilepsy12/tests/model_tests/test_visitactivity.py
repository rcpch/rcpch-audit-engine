import time

import pytest

from epilepsy12.models import (
    VisitActivity,
)


# @pytest.mark.django_db
# def test_visitActivity(e12User_GOSH, client):
#     """
#     Test that visit activity logging works, using e12User_GOSH fixture
#     """

#     client.force_login(e12User_GOSH)

#     visit_activity = VisitActivity.objects.all()

#     time.sleep(1)

#     client.force_login(e12User_GOSH)

#     assert len(visit_activity) == 2
#     assert visit_activity[1].activity_datetime > visit_activity[0].activity_datetime
