from typing import Literal
import datetime

import pytest

from epilepsy12.models import Case, Organisation, Site


@pytest.mark.django_db
@pytest.fixture()
def new_e12case_factory():
    """
    Factory fn which returns a new case. See definition for available options.
    """

    def create_e12case(
        nhs_number: str = "4799637827",
        first_name: str = "Thomas",
        surname: str = "Anderson",
        sex: int = 1,
        date_of_birth: datetime.date = datetime.date(1964, 9, 2),
        ethnicity: str = "A",
        organisation=Organisation.objects.get(ODSCode="RP401"),
        locked=False,
    ):
        new_case = Case.objects.create(
            nhs_number=nhs_number,
            first_name=first_name,
            surname=surname,
            date_of_birth=date_of_birth,
            ethnicity=ethnicity,
            locked=locked,
        )
        
        new_site = Site.objects.create(
            organisation=organisation,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            case=new_case,
        )

        return new_case

    return create_e12case
