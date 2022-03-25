from urllib.request import urlopen
from urllib.parse import quote
import json

baseUrl = 'http://snomed.info/sct'
edition = 'MAIN'
version = '2019-07-31'

def get_description_by_id(id):
    url = baseUrl + '/CodeSystem/$lookup?system=http://snomed.info/sct&code=' + str(id)
    response = urlopen(url).read()

    print(json.dumps(response))