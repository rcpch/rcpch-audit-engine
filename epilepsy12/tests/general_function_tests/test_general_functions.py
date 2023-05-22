"""Tests for the general functions used in E12
"""

import pytest

from epilepsy12.constants import VALID_NHS_NUMS
from epilepsy12.general_functions import validate_nhs_number


def test_constants_valid_nhs_nums():
    """Runs `validate_nhs_number` through the VALID_NHS_NUMS constants list, ensuring all are valid"""
    for num in VALID_NHS_NUMS:
        assert validate_nhs_number(num)["valid"]


def test_valid_nhs_number_function_works():
    """Runs `validate_nhs_number` through 2 lists:
    1) valid_nhs_numbers, asserts ALL return True
    2) invalid_nhs_numbers, asserts ALL return False
    """
    valid_nhs_numbers = VALID_NHS_NUMS[:9]
    invalid_nhs_numbers = [
        "969 003 9564",
        "969 003 9565",
        "969 003 9566",
        "434 151 9744",
        "434 151 9745",
        "434 151 9746",
        "025 845 8594",
        "025 845 8595",
        "025 845 8596",
    ]

    for num in valid_nhs_numbers:
        assert validate_nhs_number(num)["valid"]
    for num in invalid_nhs_numbers:
        assert not validate_nhs_number(num)["valid"]
