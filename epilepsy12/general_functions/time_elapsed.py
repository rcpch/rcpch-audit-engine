from dateutil.relativedelta import relativedelta
import math


def handle_interval(interval, singular_name):
    if interval == 1:
        return f"1 {singular_name}"
    elif interval > 1:
        return f"{interval} {singular_name}s"
    else:
        return ""


def stringify_time_elapsed(start_date, end_date):
    """
    Calculated field. Returns time elapsed between two dates as a string.
    """
    if end_date and start_date:
        elapsed = relativedelta(end_date, start_date)
        # Initialise empty string
        string_delta = ""

        # >= 1 year return "y years, m months"
        if elapsed.years >= 1:
            string_delta += handle_interval(elapsed.years, "year")
            if elapsed.months > 0:
                string_delta += f', {handle_interval(elapsed.months, "month")}'
            return string_delta

        # 0 years, 0 - 12 months
        else:
            # >1 month return "m months"
            if elapsed.months > 0:
                string_delta += handle_interval(elapsed.months, "month")
            # <1 month return "d days"
            else:
                if elapsed.weeks > 0:
                    string_delta += handle_interval(elapsed.weeks, "week")
                else:
                    if elapsed.days > 0:
                        string_delta += handle_interval(elapsed.days, "day")
                    else:
                        string_delta += "Same day"
            return string_delta

    else:
        raise ValueError("Both start and end dates must be provided")

def rcpch_requested_time_elapsed(start_date, end_date):
    """
    Calculated field. Returns time elapsed between two dates.

    If less than 2 years of difference, time elapsed is returned in months
    
    If greater than 2 years of difference, time elapseed is returned in years

    Note - elapsed.months cannot be larger than 12, as this value then moves over to elapsed.years + 1
    """
    if end_date and start_date:
        elapsed = relativedelta(end_date, start_date)
        string_delta = ""

        # <= 2 years return months
        if elapsed.years <= 2:
            if elapsed.years == 1:
                # Adds 12 to elapsed.months to represent a year in months
                # Returns data in months

                string_delta += handle_interval(elapsed.months+12, "month")
                return string_delta 
            else:
                string_delta += handle_interval(elapsed.months, "month")
                return string_delta

        else:
            # Returns data in years
            string_delta += handle_interval(elapsed.years, "year")
            return string_delta
    else:
        raise ValueError("Both start and end dates must be provided")