# python / django imports
from datetime import date
from django.core.exceptions import ValidationError

# RCPCH imports
from .general_functions.nhs_number import validate_nhs_number


def nhs_number_validator(number_to_validate):
    """
    Validates an NHS number
    """
    validation = validate_nhs_number(number_to_validate=number_to_validate)
    if validation["valid"]:
        return number_to_validate
    else:
        raise ValidationError(validation["message"])


def epilepsy12_date_validator(
    first_date: date() = None,
    second_date: date() = None,
    earliest_allowable_date: date() = None,
):
    """
    Validator for Epilepsy12 dates
    Base validation is that:
    1. At least one date must be supplied
    2. No date may be in the future
    3. No date may be before the earliest allowable date
    4. if supplied, second_date must be after first_date
    """

    if first_date and second_date:
        # both dates supplied
        if first_date > date() or second_date > date():
            raise ValidationError("Neither date can be in the future!")

    elif first_date:
        # only first_date supplied
        if first_date > date():
            raise ValidationError(
                f"Date supplied ({first_date}) cannot be in the future for this measure!"
            )
        if earliest_allowable_date:
            if earliest_allowable_date > first_date:
                raise ValidationError(
                    f"Date supplied ({first_date}) cannot be before {earliest_allowable_date}!"
                )
    elif second_date:
        # only second_date supplied
        if second_date > date():
            raise ValidationError(
                f"Date supplied ({second_date}) cannot be in the future for this measure!"
            )
        if earliest_allowable_date:
            if earliest_allowable_date > second_date:
                raise ValidationError(
                    f"Date supplied ({second_date}) cannot be before {earliest_allowable_date}!"
                )
    else:
        # no dates supplied
        raise ValidationError("At least one date must be supplied!")
