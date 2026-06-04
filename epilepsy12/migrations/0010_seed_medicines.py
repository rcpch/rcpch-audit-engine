# Python
import logging

# Third-party Imports
from django.db import migrations

# RCPCH Imports
from ..constants import SNOMED_BENZODIAZEPINE_TYPES, SNOMED_ANTIEPILEPSY_MEDICINE_TYPES

# Logging setup
logger = logging.getLogger(__name__)

import json
import os

with open(os.path.abspath("epilepsy12/constants/medicines.json"), "r") as f:
    medicines_data = json.load(f)


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
    logger.info(
        "\033[33m Seeding all the medicines from SNOMED and local Epilepsy12 list... \033[33m",
    )
    for medicine in medicines_data:
        if Medicine.objects.filter(medicine_name=medicine["medicine_name"]).exists():
            logger.info(f"{medicine['medicine_name']} exists. Skipping...")
        else:
            is_rescue = False
            if medicine["medicine_name"] in [
                benzo[1] for benzo in SNOMED_BENZODIAZEPINE_TYPES
            ]:
                is_rescue = True
            elif medicine["medicine_name"] in [
                aem[1] for aem in SNOMED_ANTIEPILEPSY_MEDICINE_TYPES
            ]:
                is_rescue = False
            new_medicine = Medicine(
                medicine_name=medicine["medicine_name"],
                is_rescue=is_rescue,
                conceptId=medicine["conceptId"],
                term=medicine["term"],
                preferredTerm=medicine["preferredTerm"],
            )
            try:
                new_medicine.save()
            except Exception as e:
                logger.info(f"Medicine {medicine['medicine_name']} not added. {e}")

    logger.info("All medicines added.")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0009_seed_comorbidities"),
    ]

    operations = [migrations.RunPython(seed_medicines)]
