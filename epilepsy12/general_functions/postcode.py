import requests


def is_valid_postcode(postcode):

    url = f"https://api.postcodes.io/postcodes/{postcode}/validate"
    response = requests.get(url=url)
    if response.status_code == 404:
        print("Postcode validation failure. Could not validate postcode.")
        return False
    else:
        return response.json()["result"]
