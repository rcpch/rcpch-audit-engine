# standard imports
import os

# third party imports
from django.conf import settings
from django.views.static import serve

# RCPCH imports

PROJECT_ROOT = getattr(settings, 'BASE_DIR', None)
DOCUMENTATION_STATIC_FILES_DIR = os.path.join(PROJECT_ROOT, 'staticfiles/docs-site')

def docs(request, path):
    """
    Serves static documentation site from static file folder.
    """
    if path == '':
        path = 'index.html'

    return serve(
        request,
        path,
        DOCUMENTATION_STATIC_FILES_DIR)
