# python imports
from dateutil.relativedelta import relativedelta
from datetime import date

# django imports

# E12 imports


def check_has_completed_one_year_of_care(registration_instance) -> bool:
    """
    Helper fn testing if child has received a year of epilepsy care, defined as 1 year elapsed on day function called from first paediatric assessment date
    returns boolean
    """
    if registration_instance.first_paediatric_assessment_date > date.today():
        raise Exception("The first paediatric assessment date cannot be in the future!")

    time_elapsed = relativedelta(
        date.today(), registration_instance.first_paediatric_assessment_date
    )

    if time_elapsed.years >= 1:
        return True
    else:
        return False
