from random import randrange
from datetime import timedelta


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    Thanks to Boris Verkihovsky (https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates)
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
