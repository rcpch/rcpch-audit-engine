import requests
from ..constants import UNKNOWN_POSTCODES


def is_valid_postcode(postcode):
    """
    Test if valid postcode using api.postcodes.io 
    Allow any no fixed abode etc standard codes
    """

    # convert to upper case and remove spaces
    formatted = postcode.upper().replace(' ', '')
    # look for unknown postcodes
    unknown = [code for code in UNKNOWN_POSTCODES if code.replace(
        ' ', '') == formatted]
    if len(unknown) > 0:
        return True

    # check against API
    url = f"https://api.postcodes.io/postcodes/{postcode}/validate"
    response = requests.get(url=url)
    if response.status_code == 404:
        print("Postcode validation failure. Could not validate postcode.")
        return False
    else:
        return response.json()["result"]
