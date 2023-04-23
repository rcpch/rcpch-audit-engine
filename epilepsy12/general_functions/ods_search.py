from django.conf import settings
import requests


def fetch_ods(ods_code):
    url = f"{settings.NHS_ODS_API_URL}&search={ods_code}&searchFields=ODSCode"
    response = requests.get(url, headers={
                            "subscription-key": f"{settings.NHS_ODS_API_KEY}"})

    if response.status_code == 404:
        print("Could not get ODS data from server...")
        return None

    serialised = response.json()["value"][0]

    return serialised
