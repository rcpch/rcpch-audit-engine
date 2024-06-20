import os
import requests

# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

def get_azure_token(client_id):
    url = 'http://169.254.169.254/metadata/identity/oauth2/token'

    params = {
        'api-version': '2018-02-01',
        'resource': 'https://ossrdbms-aad.database.windows.net',
        'client_id': client_id
    }

    headers = {
        'Metadata': 'true'
    }

    resp = requests.get(url=url, params=params, headers=headers)
    data = resp.json()

    return data.access_token


database_config = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": os.environ.get("E12_POSTGRES_DB_NAME"),
    "USER": os.environ.get("E12_POSTGRES_DB_USER"),
    "PASSWORD": os.environ.get("E12_POSTGRES_DB_PASSWORD"),
    "HOST": os.environ.get("E12_POSTGRES_DB_HOST"),
    "PORT": os.environ.get("E12_POSTGRES_DB_PORT"),
}

AZURE_IDENTITY_CLIENT_ID = os.environ.get('AZURE_IDENTITY_CLIENT_ID')

if AZURE_IDENTITY_CLIENT_ID:
    database_config["PASSWORD"] = get_azure_token(AZURE_IDENTITY_CLIENT_ID)
    database_config["OPTIONS"] = {'sslmode': 'require'}