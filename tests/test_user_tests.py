import pytest

from django.contrib.auth import get_user_model
from epilepsy12.models import HospitalTrust


@pytest.mark.django_db
def test_when_new_Epilepsy12User_is_created():
    
    ########
    # 1. ARRANGE
    ########
    
    # user_details_dict
    user_details = {
        
    }
    
    # set up objects
    #get HT with "OrganisationName": "Great Ormond Street Hospital"
    hospital_trust =  HospitalTrust.objects.filter(OrganisationName__contains = 'Ormond')
    
    db = get_user_model()

    ########
    # 2. ACT
    ########
    user = db.objects.create_user(
        email="testuser@epilepsy12.com",
        username="epilepsy12user",
        password="epilepsy12password",
        title=4,
        first_name="Henry",
        surname="Gastaut",
        role=1,
        hospital_trust=hospital_trust,
    )

    ######## 
    # 3. ASSERT
    ########
    assert user.email == "testuser@epilepsy12.com"