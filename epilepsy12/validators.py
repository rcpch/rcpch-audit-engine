# python / django imports
import re
from datetime import date

# django imports
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# 3rd party imports

# RCPCH imports


def epilepsy12_date_validator(
    first_date: date = None,
    second_date: date = None,
    earliest_allowable_date: date = None,
) -> bool:
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
        if first_date > date.today() or second_date > date.today():
            raise ValueError("Neither date can be in the future!")
        if earliest_allowable_date:
            if earliest_allowable_date > first_date:
                raise ValueError(
                    f"Date supplied ({first_date}) cannot be before {earliest_allowable_date}!"
                )
            elif earliest_allowable_date > second_date:
                raise ValueError(
                    f"Date supplied ({second_date}) cannot be before {earliest_allowable_date}!"
                )
        if second_date < first_date:
            raise ValueError(
                f"Date supplied ({second_date}) cannot be before {first_date}!"
            )
        return True

    elif first_date:
        # only first_date supplied
        if first_date > date.today():
            raise ValueError(
                f"Date supplied ({first_date}) cannot be in the future for this measure!"
            )
        if earliest_allowable_date:
            if earliest_allowable_date > first_date:
                raise ValueError(
                    f"Date supplied ({first_date}) cannot be before {earliest_allowable_date}!"
                )
        return True
    elif second_date:
        # only second_date supplied
        if second_date > date.today():
            raise ValueError(
                f"Date supplied ({second_date}) cannot be in the future for this measure!"
            )
        if earliest_allowable_date:
            if earliest_allowable_date > second_date:
                raise ValueError(
                    f"Date supplied ({second_date}) cannot be before {earliest_allowable_date}!"
                )
        return True
    else:
        # no dates supplied
        raise ValueError("At least one date must be supplied!")


def not_in_the_future_validator(value):
    """
    model level validator to prevent persisting a date in the future
    """
    if value <= date.today():
        return value
    else:
        raise ValidationError("Dates cannot be in the future.")


class CapitalAndSymbolValidator:
    def __init__(
        self,
        number_of_capitals=1,
        number_of_symbols=1,
        symbols="~!@#$%^&*()+:;'[]",
    ):
        self.number_of_capitals = number_of_capitals
        self.number_of_symbols = number_of_symbols
        self.symbols = symbols

    def validate(self, password, user=None):
        capitals = [char for char in password if char.isupper()]
        symbols = [char for char in password if char in self.symbols]
        if len(capitals) < self.number_of_capitals:
            raise ValidationError(
                _(
                    "This password must contain at least %(min_length)d capital letters."
                ),
                code="password_too_short",
                params={"min_length": self.number_of_capitals},
            )
        if len(symbols) < self.number_of_symbols:
            raise ValidationError(
                _("This password must contain at least %(min_length)d symbols."),
                code="password_too_short",
                params={"min_length": self.number_of_symbols},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(number_of_capitals)d capital letters and %(number_of_symbols) symbols."
            % {
                "number_of_capitals": self.number_of_capitals,
                "number_of_symbols": self.number_of_symbols,
            }
        )
