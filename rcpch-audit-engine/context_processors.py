import os 

def export_vars(request):
    data = {}
    data['GIT_HASH'] = os.environ['GIT_HASH']
    return data