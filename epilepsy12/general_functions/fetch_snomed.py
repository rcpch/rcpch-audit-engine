# standard imports
import logging
import requests

# third party imports
from django.conf import settings

# RCPCH imports
from ..constants import BENZODIAZEPINE_TYPES, ANTIEPILEPSY_MEDICINE_TYPES

# Logging setup
logger = logging.getLogger(__name__)


def fetch_ecl(ecl):
    """
    accepts a SNOMED ECL and returns a concept
    """
    search_url = f"{settings.RCPCH_HERMES_SERVER_URL}/search?constraint={ecl}"
    response = requests.get(search_url)

    if response.status_code == 404:
        logger.warning("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised


def fetch_concept(concept_id):
    """
    Returns a SNOMED concept from the RPCH Hermes API against a concept id
    """
    search_url = f"{settings.RCPCH_HERMES_SERVER_URL}/concepts/{concept_id}/extended"

    response = requests.get(search_url)

    if response.status_code == 404:
        logger.warning("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    return serialised


def fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set():
    """
    Hits the RPCH Hermes API and returns the paediatric neurodisability refset
    """
    search_url = f"{settings.RCPCH_HERMES_SERVER_URL}/expand?ecl=^999001751000000105"
    response = requests.get(search_url)

    if response.status_code == 404:
        logger.warning("Could not get SNOMED data from server...")
        return None

    # filters out Autism-related entries
    response_no_asd = [
        item for item in response.json() if item["conceptId"] != 35919005
    ]

    return response_no_asd
