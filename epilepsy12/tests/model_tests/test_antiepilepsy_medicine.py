"""Tests for AntieEpilepsyMedicine model
"""
# Standard imports
from datetime import date

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    AntiEpilepsyMedicine,
)


@pytest.mark.django_db
def test_antiepilepsy_pregnancy_checks_set_only_when_female_child_bearing_age(
    e12_case_factory,
    e12_registration_factory,
):
    registration_boy = e12_registration_factory(
        case__first_name="boy",
        case__sex=1,
        case__date_of_birth=date(2004, 1, 1),
    )
    management_boy = registration_boy.management

    registration_girl_childbearing = e12_registration_factory(
        case__first_name="girl",
        case__sex=2,
        case__date_of_birth=date(2004, 1, 1),
    )
    management__girl_childbearing = registration_girl_childbearing.management

    registration_girl_NOT_childbearing = e12_registration_factory(
        case__first_name="girl",
        case__sex=2,
        case__date_of_birth=date(2022, 1, 1),
    )
    management_girl_NOT_childbearing = registration_girl_NOT_childbearing.management

    assert not AntiEpilepsyMedicine.objects.filter(management=management_boy)[
        0
    ].is_a_pregnancy_prevention_programme_in_place
    assert AntiEpilepsyMedicine.objects.filter(
        management=management__girl_childbearing
    )[0].is_a_pregnancy_prevention_programme_in_place
    assert not AntiEpilepsyMedicine.objects.filter(
        management=management_girl_NOT_childbearing
    )[0].is_a_pregnancy_prevention_programme_in_place


@pytest.mark.django_db
def test_debugging(
    e12_case_factory,
    e12_registration_factory,
    e12_management_factory,
):
    reg = e12_registration_factory(case__first_name="tester")
    print(reg.case.first_name)
