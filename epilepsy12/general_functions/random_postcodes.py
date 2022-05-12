import requests


def generate_postcodes(requested_number: int):
    """
    returns random postcodes
    accepts requested_nunmber
    """
    postcodes = []
    for index in range(1, requested_number):
        url = "https://api.postcodes.io/random/postcodes"
        response = requests.get(url=url)

        if response.status_code == 404:
            print("Could not get LSOA from postcode.")
            return None

        serialised = response.json()
        postcode = serialised['result']['postcode']
        postcodes.append(postcode)
    return postcodes
