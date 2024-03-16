# standard imports
import logging
import requests
from pprint import pprint

# third party imports
from django.conf import settings

# RCPCH imports
from django.apps import apps

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
    search_url = f"{settings.RCPCH_HERMES_SERVER_URL}/expand?ecl={concept_id}"

    response = requests.get(search_url)

    if response.status_code == 404:
        logger.warning("Could not get SNOMED data from server...")
        return None

    serialised = response.json()

    print(serialised)

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


def add_cause_by_sctid_to_database(sct_id: int):
    """
    Function that accepts an SCTID (sanctioned by the E12 team), uses this to get the SNOMED concept
    and persist this in the database.
    """
    EpilepsyCause = apps.get_model("epilepsy12", "EpilepsyCause")
    error_message = None
    try:
        snomed_concept = fetch_concept(concept_id=sct_id)[0]
    except Exception as error:
        error_message = error
        return {"success": False, "concept": None, "error": error_message}

    if EpilepsyCause.objects.filter(conceptId=snomed_concept["conceptId"]).exists():
        # duplicate conceptId
        return {
            "success": False,
            "concept": snomed_concept["conceptId"],
            "error": "Duplicate. Item not saved.",
        }
    else:
        new_cause = EpilepsyCause(
            conceptId=snomed_concept["conceptId"],
            term=snomed_concept["term"],
            preferredTerm=snomed_concept["preferredTerm"],
        )
        try:
            new_cause.save()
        except Exception as e:
            logger.info(
                f"Epilepsy cause {snomed_concept['preferredTerm']} not added. {e}"
            )
            return {"success": False, "concept": None, "error": e}
    logger.info(f"{snomed_concept['preferredTerm']} added")
    return {"success": True, "concept": snomed_concept, "error": None}


def add_epilepsy_cause_list_by_sctid(extra_concept_ids: list):
    """
    Adds a new list of epilepsy causes
    Duplicates will be ignored
    Accepts a list of SCT IDs
    **Note the SCT ID should be added to the extra_concept_ids list in migration 0006**
    """
    index = 0

    for sct_id in extra_concept_ids:
        response = add_cause_by_sctid_to_database(sct_id=sct_id)
        if response["success"]:
            index += 1
        else:
            logger.error(response["error"])
    if len(extra_concept_ids) == index:
        info_string = f"{index} extra concepts added."
        logger.info(info_string)
    else:
        warning_string = f"Only {index} extra concepts from an expected total {len(extra_concept_ids)} added. Check logs for errors."
        logger.warning(warning_string)
