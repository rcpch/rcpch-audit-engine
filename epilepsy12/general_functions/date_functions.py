from datetime import date, timedelta


def next_weekday(d, weekday):
    # Thanks to Phihag for this snippet
    # https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-date
    # 0=Monday
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def first_tuesday_in_january(year):
    jan_first = date(year, 1, 1)
    if jan_first.weekday() == 1:
        # Jan first of year supplied is a Tuesday
        first_tuesday = jan_first
    else:
        first_tuesday = next_weekday(jan_first, 1)
    return first_tuesday
