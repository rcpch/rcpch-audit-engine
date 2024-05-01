import os
from azure.identity import DefaultAzureCredential

# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

database_config = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": os.environ.get("AZURE_POSTGRESQL_NAME") or os.environ.get("E12_POSTGRES_DB_NAME"),
    "USER": os.environ.get("AZURE_POSTGRESQL_USER") or os.environ.get("E12_POSTGRES_DB_USER"),
    "PASSWORD": os.environ.get("E12_POSTGRES_DB_PASSWORD"),
    "HOST": os.environ.get("AZURE_POSTGRESQL_HOST") or os.environ.get("E12_POSTGRES_DB_HOST"),
    "PORT": os.environ.get("E12_POSTGRES_DB_PORT"),
}

if not database_config["PASSWORD"]:
    database_config["PASSWORD"] = DefaultAzureCredential().get_token('https://ossrdbms-aad.database.windows.net/.default').token
    database_config["OPTIONS"] = {'sslmode': 'require'}
