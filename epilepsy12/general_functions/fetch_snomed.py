
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

    ecl_url = f'https://snomed-server-fztgv.ondigitalocean.app/v1/snomed/expand?ecl={VALID_SYNTAX[syntax]}{sctid}'

    search_url = f'https://snomed-server-fztgv.ondigitalocean.app/v1/snomed/search?s={search_string}\&constraint=<64572001'

    response = requests.get(ecl_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()
    print(serialised)

    for index, term in enumerate(serialised):
        print(term['term'])


def snomed_search(search_term):
    search_url = f'https://snomed-server-fztgv.ondigitalocean.app/v1/snomed/search?s={search_term}\&constraint=<64572001'

    response = requests.get(search_url)

    if response.status_code == 404:
        print("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised
