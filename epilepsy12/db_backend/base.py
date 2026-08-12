"""
Custom PostGIS database backend that authenticates using an Azure Entra ID
(managed identity) access token instead of a static password.

Django reads the connection password once, at connection time, via
``get_connection_params``. By overriding that hook we inject a fresh token
whenever a *new* connection is opened, avoiding the "access token has expired"
errors that occur when a token acquired at process startup later expires.

Only the ``password`` key is swapped in; everything else is inherited from the
stock PostGIS backend by calling ``super().get_connection_params()``, keeping
our coupling to Django internals as small as possible.

Token auth is enabled per-connection via the ``USE_AAD_TOKEN`` key in the
database settings dict (see ``settings.py``). When it is not set, the backend
behaves exactly like the stock backend and uses the configured ``PASSWORD``.
"""

import logging

from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISWrapper,
)

logger = logging.getLogger(__name__)

# https://learn.microsoft.com/azure/postgresql/flexible-server/how-to-configure-sign-in-azure-ad-authentication
_AAD_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

# A single, reused credential. azure-identity caches tokens *on the credential
# instance*, so reusing one instance is what makes that cache effective:
# get_token() then only reaches out to the Azure IMDS endpoint when the token
# is near expiry, and is a cheap in-memory hit the rest of the time. Building a
# new credential per connection (as a naive implementation would) throws the
# cache away every time and hammers IMDS on every connection. Created lazily so
# non-token deployments never build it.
_credential = None


def _get_token():
    global _credential

    if _credential is None:
        from azure.identity import DefaultAzureCredential

        _credential = DefaultAzureCredential()

    return _credential.get_token(_AAD_SCOPE).token


class DatabaseWrapper(PostGISWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()

        if self.settings_dict.get("USE_AAD_TOKEN"):
            try:
                params["password"] = _get_token()
            except Exception:
                logger.exception("Failed to acquire an Entra ID token for Postgres")
                raise

        return params
