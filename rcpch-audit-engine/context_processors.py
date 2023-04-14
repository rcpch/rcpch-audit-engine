import os 

def export_vars(request):
    """
    Gets the `GIT_HASH` environment variable, created in GitHub Actions workflow, inserts into all templates.
    """
    data = {}
    data['GIT_HASH'] = os.environ.get('GIT_HASH')
    if not data['GIT_HASH']:
        data['GIT_HASH'] = 'Hash not found.'
    return data