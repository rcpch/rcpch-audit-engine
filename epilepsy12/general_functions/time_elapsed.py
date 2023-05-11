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
            string_delta += f", {handle_interval(elapsed.months, 'month')}"
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
                        string_delta += f"{handle_interval(elapsed.days, 'day')}"
                    else:
                        string_delta += "Same day"
            return string_delta

    else:
        raise ValueError("Both start and end dates must be provided")
