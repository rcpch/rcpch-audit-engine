import requests
# from requests import request
from .postcode import valid_postcode
import json

"""
Steps to calculate IMD

1. identify LSOA from postcode - cand do this from https://api.postcodes.io/postcodes/
2. Use the LSOA to get the IMD - cand do this from 
"""


def imd_for_postcode(user_postcode: str) -> int:

    # TODO #26 validate the postcode, strip spaces
    postcode = user_postcode.replace(" ", "")

    url = "https://api.postcodes.io/postcodes/"+postcode
    response = requests.get(url=url)

    if response.status_code == 404:
        print("Could not get LSOA from postcode.")
        return None

    serialised = response.json()
    lsoa = serialised["result"]["codes"]["lsoa"]

    # note for this to work Mark Wardle's Deprivare needs to be running on port 8080
    # Thank you Mark for this remarkable tool (https://github.com/wardle/deprivare)

    deprivare_url = "http://rcpch-deprivare.uksouth.azurecontainer.io:8080/v1/uk/lsoa/"+lsoa

    deprivare_response = requests.get(
        url=deprivare_url, headers={"Content-Type": 'application/json; charset=utf-8'})
    result = deprivare_response.json(
    )["uk-composite-imd-2020-mysoc/UK_IMD_E_pop_quintile"]

    return result
