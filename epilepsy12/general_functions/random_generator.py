from random import randrange
from datetime import timedelta, date


def random_date(start: date, end: date):
    """
    returns a random date between two dates

    Note if end and start dates supplied are the same, the start date is returned
    """
    if end == start:
        return start
    elif start > end:
        raise Exception(
            "Cannot generate a random date if end date supplied is before start date."
        )
    else:
        delta = end - start
        random_days = randrange(0, delta.days)
        return start + timedelta(days=random_days)
