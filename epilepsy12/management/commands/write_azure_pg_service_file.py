import os
import requests
from django.core.management.base import BaseCommand

# https://www.postgresql.org/docs/current/libpq-pgservice.html
#
# Allows us to periodically update the access token for Entra ID
# authenticated connections in Azure (triggering this command from cron).
# 
# Django specifically does not allow you to update settings at
# runtime so we store the connection details in a separate file.

class Command(BaseCommand):
    help = "Generate a Postgres service file to use an Azure managed identity to authenticate with the database."
    
    def fetch_azure_token(self):
        url = 'http://169.254.169.254/metadata/identity/oauth2/token'

        params = {
            'api-version': '2018-02-01',
            'resource': 'https://ossrdbms-aad.database.windows.net'
        }

        headers = {
            'Metadata': 'true'
        }

        resp = requests.get(url=url, params=params, headers=headers)
        data = resp.json()

        return data['access_token']

    def handle(self, *args, **options):
        service = os.environ.get('E12_POSTGRES_SERVICE') or 'e12'
        service_file = os.environ.get('E12_POSTGRES_DB_SERVICE_FILE')

        if not service_file:
            print('Not using service file, will read database password from the env file')
            return

        password = self.fetch_azure_token()

        with open(service_file, "w") as f:
            f.write(f"""[#{service}]
host={os.environ['E12_POSTGRES_DB_HOST']}
user={os.environ['E12_POSTGRES_DB_USER']}
password={password}
dbname={os.environ['E12_POSTGRES_DB_NAME']}
sslmode=require
""")