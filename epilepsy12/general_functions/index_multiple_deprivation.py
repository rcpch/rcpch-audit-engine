"""
Calculates the index of multiple deprivation for a given postcode
"""

# Standard imports
import logging
import requests

# Third party imports
from django.conf import settings

# Logging setup
logger = logging.getLogger(__name__)


def imd_for_postcode(user_postcode: str, year: int = 2019) -> int | None:
    """
    Makes an API call to the RCPCH Census Platform with postcode, quantile_type and IMD year to get the quantile for the given postcode and quantile type.
    The English IMD have 2019 and 2025 versions, the Welsh only 2019.
    Postcode - can have spaces or not - this is processed by the API
    Quantile - this is an integer representing what quantiles are requested (eg quintile, decile etc)
    Returns the quantile for the given postcode and quantile type, or None if there was an error
    """
    if year not in [2019, 2025]:
        logger.error("Invalid year %s for IMD. Must be 2019 or 2025", year)
        return None
    response = requests.get(
        url=f"{settings.RCPCH_CENSUS_PLATFORM_URL}/index_of_multiple_deprivation_quantile?postcode={user_postcode}&quantile=5&year={year}",
        headers={"Subscription-Key": f"{settings.RCPCH_CENSUS_PLATFORM_TOKEN}"},
        timeout=10,  # times out after 10 seconds
    )

    if response.status_code != 200:
        logger.error(
            "Could not get deprivation score for %s. Response status %s",
            user_postcode,
            response.status_code,
        )
        return None

    return response.json()["result"]["data_quantile"]


def recalculate_imd_for_case(case) -> None:
    """
    Recalculates the IMD quintile for a Case and persists only that field.

    No-op if any of the following are true:
    - case.postcode is absent or an unknown/placeholder postcode
    - case has no Registration yet, or Registration.cohort is not yet set

    Uses queryset .update() rather than case.save() to avoid re-triggering
    Case.post_save signals and coordinate lookups.
    Also updates the in-memory instance so the caller sees the new value.
    """
    from ..constants import UNKNOWN_POSTCODES_NO_SPACES

    postcode = case.postcode
    if not postcode:
        return

    normalised = postcode.replace(" ", "").replace("-", "").upper()
    if normalised in UNKNOWN_POSTCODES_NO_SPACES:
        return

    try:
        registration = case.registration
    except Exception:
        # No registration exists yet — IMD will be recalculated once Registration is saved.
        return

    if registration is None or registration.cohort is None:
        return

    imd_year = 2025 if registration.cohort >= 8 else 2019

    try:
        quintile = imd_for_postcode(normalised, year=imd_year)
    except Exception as error:
        logger.exception(
            "Cannot calculate deprivation score for %s: %s", normalised, error
        )
        quintile = None

    # Use queryset update to skip Case.save() and its signals entirely.
    from django.apps import apps

    Case = apps.get_model("epilepsy12", "Case")
    Case.objects.filter(pk=case.pk).update(
        index_of_multiple_deprivation_quintile=quintile
    )
    # Keep the in-memory object consistent.
    case.index_of_multiple_deprivation_quintile = quintile
