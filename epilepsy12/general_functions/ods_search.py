import requests


def fetch_ods(ods_code):
    url = f"https://api.nhs.uk/service-search?api-version=2&search={ods_code}&searchFields=ODSCode"
    response = requests.get(url, headers={
                            "subscription-key": "###########"})

    if response.status_code == 404:
        print("Could not get ODS data from server...")
        return None

    serialised = response.json()

    return serialised
