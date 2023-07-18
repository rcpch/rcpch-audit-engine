from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, TU

def nth_tuesday_of_year(year:int, n:int)->date:
    """Returns the nth Tuesday for a given year.

    Args:
        year (int): year in which to find nth Tuesday of Jan.
        n (int): which Tuesday of Jan to return e.g. if year=2022 n=2 returns 2nd Tues of Jan; n=5 returns 1st Tues of Feb.

    Returns:
        date: nth Tuesday as date.
    """
    jan_first = date(year, 1, 1)
    return jan_first + relativedelta(weekday=TU(n))

def first_tuesday_in_january(year):
    """Fn which makes it simpler to get first Tues of Jan for a given year, if used already in codebase.
    """
    return nth_tuesday_of_year(year, n=1)
