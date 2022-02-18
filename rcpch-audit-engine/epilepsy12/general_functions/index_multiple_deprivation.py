import requests
# from requests import request
from .postcode import valid_postcode

"""
Steps to calculate IMD

1. identify LSOA from postcode - cand do this from https://api.postcodes.io/postcodes/
2. Use the LSOA to get the IMD - cand do this from 
"""

def imd_for_postcode(user_postcode: str)->int:
    
    # validate the postcode, strip spaces
    postcode=valid_postcode(user_postcode)
    
    # initialise return object
    map_object={}
    
    if(postcode.match('not matched')):
        raise Exception("Invalid postcode")
    else:
        url="https://api.postcodes.io/postcodes/"+postcode
        map_object=requests.get(url=url)
        lsoa = map_object.result.codes.lsoa

        # note for this to work Mark Wardle's Deprivare needs to be running on port 8082
        # Thank you Mark for this remarkable tool
        deprivare_url="http://localhost:8082/v1/uk/lsoa/"+lsoa

        deprivation_data=requests.get(url=deprivare_url)
        print(deprivation_data)

