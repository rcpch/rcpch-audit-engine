"""Fn which returns True if object has all specified attributes.
"""


def has_all_attributes(obj: object, attributes: list[str]) -> bool:
    # loop through and check each attribute contained in object. If ANY not found, return False.
    for attr in attributes:
        if not hasattr(obj, attr):
            return False
    return True
