from random import randrange
from datetime import timedelta, date


def random_date(start: date, end: date):
    delta = end - start
    random_days = randrange(0, delta.days)
    return start + timedelta(days=random_days)
