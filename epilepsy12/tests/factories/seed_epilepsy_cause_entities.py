# python imports

# django imports

# third party imports
import pytest

# RCPCH imports
from epilepsy12.models import EpilepsyCauseEntity
from epilepsy12.general_functions.fetch_snomed import fetch_ecl


@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_epilepsy_causes_fixture(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        if not EpilepsyCauseEntity.objects.exists():
            ecl = "<< 363235000"
            # calls the rcpch deprivare server for a list of causes using ECL query language
            epilepsy_causes = fetch_ecl(ecl)
            for cause in epilepsy_causes:
                new_cause = EpilepsyCauseEntity(
                    conceptId=cause["conceptId"],
                    term=cause["term"],
                    preferredTerm=cause["preferredTerm"],
                    description=None,
                    snomed_ct_edition=None,
                    snomed_ct_version=None,
                    icd_code=None,
                    icd_version=None,
                    dsm_code=None,
                    dsm_version=None,
                )
                try:
                    new_cause.save()
                    index += 1
                except Exception as e:
                    print(f"Epilepsy cause {cause['preferredTerm']} not added. {e}")
            print(f"{index} epilepsy causes added")
        else:
            print("Epilepsy causes already seeded. Skipping...")
