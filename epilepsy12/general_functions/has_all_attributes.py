"""Fn which returns True if object has all specified attributes.
"""


def has_all_attributes(obj: object, attributes: list[str]) -> bool:
    """
    Check if the given object has all the specified attributes.

    Args:
        obj (object): The object to check for attributes.
        attributes (list[str]): A list of attribute names to check.

    Returns:
        bool: True if the object has all the specified attributes, False otherwise.
    """
    for attr in attributes:
        if not hasattr(obj, attr):
            return False
    return True
