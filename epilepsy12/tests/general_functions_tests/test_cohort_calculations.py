# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.general_functions import cohort_number_from_enrolment_date


def test_cohort_number_from_enrolment_date_returns_correct_num(e12_case_factory):
    """
    Test that cohort_number_from_enrolment_date() returns correct num, given different Date of First Paediatric Assessment (DoFPAs).
    
    The latest DoFPA for a cohort is 30th Nov of a given year. For 2023, it will be Cohort 6 until 30th Nov 2023, then Cohort 7 1st Dec 2023-30th Nov 2024.
    """
    
    expected_cohort_for_dates = (
        (date(2023, 11, 30), 5),
    )
    
    