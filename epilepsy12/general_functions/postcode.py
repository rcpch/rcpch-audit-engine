import requests
import logging

from django.conf import settings
from ..constants import UNKNOWN_POSTCODES_NO_SPACES

# Logging setup
logger = logging.getLogger(__name__)


def is_valid_postcode(postcode: str) -> bool:
    """
    Returns True if postcode valid.
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(" ", "")
    # look for unknown postcodes
    if formatted in UNKNOWN_POSTCODES_NO_SPACES:
        return True

    # check against API
    url = f"{settings.POSTCODE_API_BASE_URL}/postcodes/{postcode}"

    response = requests.get(url=url)

    if response.status_code == 200:
        return True

    # Only other possibility should be 404, but handle any other status code
    logger.error(
        f"Postcode validation failure. Could not validate postcode at {url}. {response.status_code=}"
    )
    return False


def coordinates_for_postcode(postcode: str) -> bool:
    """
    Returns longitude and latitude for a valide postcode.
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(" ", "")
    formatted = postcode.upper().replace("-", "")
    # look for unknown postcodes
    if formatted in UNKNOWN_POSTCODES_NO_SPACES:
        return True

    # check against API
    url = f"{settings.POSTCODE_API_BASE_URL}/postcodes/{postcode}"

    response = requests.get(url=url)

    if response.status_code == 200:
        location = response.json()["data"]["attributes"]["location"]
        return location["lon"], location["lat"]

    # Only other possibility should be 404, but handle any other status code
    logger.error(
        f"Postcode validation failure. Could not validate postcode at {url}. {response.status_code=}"
    )
    return None


def return_random_postcode(country_boundary_identifier: str):
    """Returns random postcode (str) inside country_boundary_identifier or `None` if invalid."""
    url = f"{settings.POSTCODE_API_BASE_URL}/areas/{country_boundary_identifier}"

    response = requests.get(url=url)

    if response.status_code == 404:
        logger.error("Postcode generation failure. Could not get random postcode.")
        return None

    return response.json()["data"]["relationships"]["example_postcodes"]["data"][0][
        "id"
    ].replace(" ", "")
