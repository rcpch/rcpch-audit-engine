import requests
import os
from django.conf import settings

"""
Steps to calculate IMD

1. identify LSOA from postcode - cand do this from https://api.postcodes.io/postcodes/
2. Use the LSOA to get the IMD - cand do this from 
"""


def imd_for_postcode(user_postcode: str) -> int:
    """
    This is makes an API call to the RCPCH Census Platform with postcode and quantile_type
    Postcode - can have spaces or not - this is processed by the API
    Quantile - this is an integer representing what quantiles are requested (eg quintile, decile etc)
    """

    url = f"{settings.RCPCH_CENSUS_PLATFORM_URL}/index_of_multiple_deprivation_quantile?postcode={user_postcode}&quantile=5"

    response = requests.get(
        url=url, headers={'Subscription-Key': f'{settings.RCPCH_CENSUS_PLATFORM_TOKEN}'})

    if response.status_code != 200:
        print(f"Could not get deprivation score. {response.status_code}")
        return None

    result = response.json()['result']

    return result['data_quantile']
