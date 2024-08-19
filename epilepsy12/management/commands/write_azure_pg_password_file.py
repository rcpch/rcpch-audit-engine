import os

from django.core.management.base import BaseCommand
from azure.identity import DefaultAzureCredential

# https://www.postgresql.org/docs/current/libpq-pgpass.html
#
# Allows us to periodically update the access token for Entra ID
# authenticated connections in Azure (triggering this command from cron).
# 
# Django specifically does not allow you to update settings at
# runtime so we store the connection details in a separate file.

def write_azure_pg_password_file():
    password_file = os.environ.get('NPDA_POSTGRES_DB_PASSWORD_FILE')

    if not password_file:
        return

    password = DefaultAzureCredential().get_token("https://ossrdbms-aad.database.windows.net").token

    with open(password_file, "w") as f:
        f.write(f"*:*:*:*:{password}")
    
    # libpg silently ignores the file if it's readable by anyone else
    os.chmod(password_file, 0o600)


class Command(BaseCommand):
    help = "Generate a Postgres password file to use an Azure managed identity to authenticate with the database."

    def handle(self, *args, **options):
        write_azure_pg_password_file()
