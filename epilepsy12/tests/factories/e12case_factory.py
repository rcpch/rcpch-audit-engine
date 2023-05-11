from typing import Literal
import datetime

import pytest

from epilepsy12.models import Case


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
    ):
        return Case.objects.create(
            nhs_number=nhs_number,
            first_name=first_name,
            surname=surname,
            sex=sex,
            date_of_birth=date_of_birth,
            ethnicity=ethnicity,
        )
    return create_e12case
