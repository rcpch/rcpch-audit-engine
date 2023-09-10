import requests
from django.conf import settings
from ..constants import UNKNOWN_POSTCODES_NO_SPACES


def is_valid_postcode(postcode):
    """
    Test if valid postcode using api.postcodes.io
    Allow any no fixed abode etc standard codes
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(" ", "")
    # look for unknown postcodes
    if formatted in UNKNOWN_POSTCODES_NO_SPACES:
        return True

    # check against API
    url = f"{settings.POSTCODES_IO_API_URL}/postcodes/{postcode}/validate"

    response = requests.get(url=url)
    if response.status_code == 404:
        print("Postcode validation failure. Could not validate postcode.")
        return False
    else:
        return response.json()["result"]


def return_random_postcode():
    # get random postcode from API
    url = f"{settings.POSTCODES_IO_API_URL}/random/postcodes"

    response = requests.get(url=url)
    if response.status_code == 404:
        print("Postcode generation failure. Could not get random postcode.")
        return None
    else:
        return response.json()["result"]["postcode"]


def call_api(postcode):
    formatted = postcode.upper().replace(" ", "+")
    api = f"https://findthatpostcode.uk/postcodes/{formatted}.json"
    response = requests.get(url=api)
    if response.status_code != 200:
        return None
    r = response.json()["data"]["attributes"]["laua"]
    return r
