# Python

# Third-party Imports
from django.db import migrations

# RCPCH Imports
from ..constants import SNOMED_BENZODIAZEPINE_TYPES, SNOMED_ANTIEPILEPSY_MEDICINE_TYPES
from ..general_functions import fetch_ecl


def seed_medicines(apps, schema_editor):
    """
    This function adds medicines to the Medicine model from SNOMED and local Epilepsy12 list.

    Parameters:
    apps (list): A list of installed apps
    schema_editor (object): A database schema editor object

    Returns:
    None
    """
    Medicine = apps.get_model("epilepsy12", "Medicine")
    print(
        "\033[33m",
        "Seeding all the medicines from SNOMED and local Epilepsy12 list...",
        "\033[33m",
    )
    for benzo in SNOMED_BENZODIAZEPINE_TYPES:
        if not Medicine.objects.filter(medicine_name=benzo[1]).exists():
            # if the drug is not in the database already
            if benzo[0] not in [1001, 1002]:
                concept = fetch_ecl(benzo[0])
                new_drug = Medicine(
                    medicine_name=benzo[1],
                    is_rescue=True,
                    conceptId=concept[0]["conceptId"],
                    term=concept[0]["term"],
                    preferredTerm=concept[0]["preferredTerm"],
                )
                new_drug.save()
            else:
                # these are for options other or unknown
                new_drug = Medicine(
                    medicine_name=benzo[1],
                    is_rescue=True,
                    conceptId=None,
                    term=None,
                    preferredTerm=None,
                )
                new_drug.save()
        else:
            print(f"{benzo[1]} exists. Skipping...")
    for aem in SNOMED_ANTIEPILEPSY_MEDICINE_TYPES:
        if not Medicine.objects.filter(medicine_name=aem[1], is_rescue=False).exists():
            # if the drug is not in the database already
            if aem[0] not in [1001, 1002]:
                concept = fetch_ecl(aem[0])
                aem_drug = Medicine(
                    is_rescue=False,
                    medicine_name=aem[1],
                    conceptId=concept[0]["conceptId"],
                    term=concept[0]["term"],
                    preferredTerm=concept[0]["preferredTerm"],
                )
                aem_drug.save()
            else:
                aem_drug = Medicine(
                    medicine_name=aem[1],
                    conceptId=None,
                    term=None,
                    preferredTerm=None,
                    is_rescue=False,
                )
                aem_drug.save()
        else:
            print(f"{aem_drug[1]} exists. Skipping...")
    print("All medicines added.")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0009_seed_comorbidities"),
    ]

    operations = [migrations.RunPython(seed_medicines)]
