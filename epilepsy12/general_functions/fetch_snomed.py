
import requests


def fetch_snomed(sctid, syntax):
    """
    Makes an API call to the RCPCH hosted instance of Hermes - a SNOMED terminology server developed by @mwardle
    This function accepts a SNOMED CT ID, together with the relevant ECL syntax.

    ECL syntax options include: memberOf, descendentOf, descendentSelfOf, childOf, childSelfOf, ancestorOf, ancestorSelfOf, parentOf, parentSelfOf

    Brief syntax	Long syntax	        Description
        <!	        childOf	            Children
        <<!	        childOrSelfOf	    Concept itself and children
        <	        descendantOf	    Descendants
        <<	        descendantOrSelfOf	Concept itself and descendants
        >!	        parentOf	        Parents
        >>!	        parentOrSelfOf	    Concept itself and parents
        >	        ancestorOf	        Ascendants
        >>	        ancestorOrSelfOf	Concept itself and ascendants
        ^	        memberOf	        Members of a reference set
    """

    VALID_SYNTAX = {'conceptOnly': '', 'memberOf': '^', 'descendentOf': '<', 'descendentSelfOf': '<<', 'childOf': '<!',
                    'childSelfOf': '<<!', 'ancestorOf': '>', 'ancestorSelfOf': '>>', 'parentOf': '>!', 'parentSelfOf': '>>!'}

    if syntax not in VALID_SYNTAX:
        raise KeyError(f'This SNOMED syntax: {syntax} is wrong.')

    # epilepsy = <<84757009

    ecl_url = f'http://rcpch-hermes.uksouth.azurecontainer.io:8080/v1/snomed/expand?ecl={VALID_SYNTAX[syntax]}{sctid}'

    response = requests.get(ecl_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised


def snomed_search(search_term):
    search_url = f'http://rcpch-hermes.uksouth.azurecontainer.io:8080/v1/snomed/search?s={search_term}\&constraint=<64572001'

    response = requests.get(search_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised


def snomed_medicine_search(search_term):
    search_url = f'http://rcpch-hermes.uksouth.azurecontainer.io:8080/v1/snomed/search?s={search_term}\&constraint=<373873005'

    response = requests.get(search_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised


def fetch_concept(concept_id):
    search_url = f'http://rcpch-hermes.uksouth.azurecontainer.io:8080/v1/snomed/concepts/{concept_id}/extended'

    response = requests.get(search_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised
