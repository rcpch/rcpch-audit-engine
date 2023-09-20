import requests
from django.conf import settings
from ..constants import UNKNOWN_POSTCODES_NO_SPACES


def is_valid_postcode(postcode:str)->bool:
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
    print(f"Postcode validation failure. Could not validate postcode at {url}. {response.status_code=}")
    return False
        


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
