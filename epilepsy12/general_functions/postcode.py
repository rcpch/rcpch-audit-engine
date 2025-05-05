import requests
import logging
from random import randint
import re

from django.conf import settings
from ..constants import UNKNOWN_POSTCODES_NO_SPACES

# Logging setup
logger = logging.getLogger(__name__)


def is_valid_postcode(postcode: str, is_jersey=False) -> bool:
    """
    Returns True if postcode valid. False otherwise.
    If is_jersey is True, the postcode is validated against the Jersey postcode format - this is less
    rigorous than the API validation but is necessary since the API does not support Jersey postcodes.
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(" ", "")
    # look for unknown postcodes
    if formatted in UNKNOWN_POSTCODES_NO_SPACES:
        return True

    if is_jersey:
        return validate_jersey_postcode(value=postcode)

    # check against API
    url = f"{settings.POSTCODES_IO_API_URL}/postcodes/{postcode}"

    response = requests.get(
        url=url,
        headers={"Ocp-Apim-Subscription-Key": settings.POSTCODES_IO_API_KEY},
        timeout=10,  # times out after 10 seconds)
    )

    if response.status_code == 200:
        return True

    if response.status_code in [400, 404]:
        # Log this at error so we still email the admins about it.
        # This is to try and spot any examples where a correct postcode is marked as invalid.
        logger.error(f"Invalid postcode {postcode} from {url}. {response.status_code=}")
        return False

    # For anything else, log the error but say the postcode is valid.
    # We don't want to stop data entry if the postcode validation service is down.
    logger.error(
        f"Postcode validation failure. Could not validate postcode at {url}. {response.status_code=}"
    )
    return True


def validate_jersey_postcode(value):
    """
    Validates if the given value matches the Jersey postcode format (JE# #AA or JE###AA without spaces).
    """
    value = value.upper().replace(" ", "")  # Convert to uppercase and remove all spaces
    pattern = (
        r"^JE\d{1,2}\d[ABD-HJLNP-UW-Z]{2}$"  # Regex for Jersey postcodes without spaces
    )
    if not re.match(pattern, value):
        return False
    return True


def coordinates_for_postcode(postcode: str) -> bool:
    """
    Returns longitude and latitude for a valid postcode.
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(" ", "")
    formatted = postcode.upper().replace("-", "")
    # look for unknown postcodes
    if formatted in UNKNOWN_POSTCODES_NO_SPACES:
        return True

    # check against API
    url = f"{settings.POSTCODES_IO_API_URL}/postcodes/{postcode}"

    response = requests.get(
        url=url,
        headers={"Ocp-Apim-Subscription-Key": settings.POSTCODES_IO_API_KEY},
        timeout=10,  # times out after 10 seconds)
    )

    if response.status_code == 200:
        location = response.json()["data"]["attributes"]["location"]
        return location["lon"], location["lat"]

    # Only other possibility should be 404, but handle any other status code
    logger.error(
        f"Postcode validation failure. Could not validate postcode at {url}. {response.status_code=}"
    )
    return None


def return_random_postcode(
    country_boundary_identifier: str, is_jersey: bool = False
) -> str:
    """
    Returns random postcode (str) inside country_boundary_identifier or `None` if invalid.

    Also accepts a boolean `is_jersey` to determine if the country is Jersey. In these circumstances the postcode
    will be randomly chosen from a predefined list of Jersey postcodes since the API does not support Jersey postcodes.
    """
    JERSEY_POSTCODES = [
        "JE1 1AA",
        "JE1 1AB",
        "JE1 2BA",
        "JE2 3CD",
        "JE2 4EF",
        "JE3 5GH",
        "JE3 5IJ",
        "JE3 6KL",
        "JE3 7MN",
        "JE4 8OP",
        "JE4 8QR",
        "JE4 9ST",
        "JE1 3UV",
        "JE2 1WX",
        "JE2 2YZ",
        "JE3 3AA",
        "JE3 4BB",
        "JE3 5CC",
        "JE3 6DD",
        "JE4 7EE",
        "JE4 8FF",
        "JE1 1GG",
        "JE1 2HH",
        "JE1 3JJ",
        "JE2 4KK",
        "JE2 5LL",
        "JE2 6MM",
        "JE3 7NN",
        "JE3 8OO",
        "JE4 9PP",
        "JE1 4QQ",
        "JE1 5RR",
        "JE1 6SS",
        "JE2 7TT",
        "JE2 8UU",
        "JE3 9VV",
        "JE4 1WW",
        "JE4 2XX",
        "JE4 3YY",
        "JE4 4ZZ",
        "JE1 7AA",
        "JE1 8BB",
        "JE2 9CC",
        "JE2 1DD",
        "JE3 2EE",
        "JE3 3FF",
        "JE3 4GG",
        "JE4 5HH",
        "JE4 6JJ",
        "JE4 7KK",
    ]

    if is_jersey:
        return JERSEY_POSTCODES[randint(0, len(JERSEY_POSTCODES) - 1)]

    url = f"{settings.POSTCODES_IO_API_URL}/areas/{country_boundary_identifier}"

    response = requests.get(
        url=url,
        headers={"Ocp-Apim-Subscription-Key": settings.POSTCODES_IO_API_KEY},
        timeout=10,  # times out after 10 seconds)
    )

    if response.status_code != 200:
        logger.error(
            f"Postcode generation failure. Could not get random postcode for {country_boundary_identifier}. {response.status_code=}"
        )
        return None

    return response.json()["data"]["relationships"]["example_postcodes"]["data"][0][
        "id"
    ].replace(" ", "")


0
