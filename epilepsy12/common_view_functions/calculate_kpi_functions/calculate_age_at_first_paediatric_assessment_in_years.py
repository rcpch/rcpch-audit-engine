# python imports
from dateutil.relativedelta import relativedelta

# django imports

# E12 imports


def calculate_age_at_first_paediatric_assessment_in_years(registration_instance) -> int:
    """
    Helper fn returns age in years as int
    """
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.first_paediatric_assessment_date,
        registration_instance.case.date_of_birth,
    )

    return age_at_first_paediatric_assessment.years
