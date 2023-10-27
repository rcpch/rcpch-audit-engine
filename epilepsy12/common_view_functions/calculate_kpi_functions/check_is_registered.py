# python imports

# django imports

# E12 imports


def check_is_registered(registration_instance) -> bool:
    """
    Helper fn returns True if registered
    """
    return (
        registration_instance.first_paediatric_assessment_date is not None
        and registration_instance.eligibility_criteria_met
    )
