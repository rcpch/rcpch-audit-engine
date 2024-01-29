# Generated by Django 4.2 on 2023-04-24 14:00

# Python
import logging

# Third-party Imports
from django.db import migrations

# RCPCH Imports
from ..models import ComorbidityList
from ..general_functions import (
    fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set,
)

# Logging setup
logger = logging.getLogger(__name__)


def seed_comorbidities(apps, schema_editor):
    """
    This function seeds the Comorbidity model with SNOMED CT definitions and codes for epilepsy causes.
    It should be run periodically to compare the stored value in the database and update records if there is a change.

    Parameters:
        apps (list): A list of installed apps
        schema_editor (object): A database schema editor object

    Returns:
        None
    """
    logger.info(
        "\033[33m Seeding comorbidities from paediatric neurodisability reference set... \033[33m",
    )
    if ComorbidityList.objects.count() >= 312:
        logger.info(f"{ComorbidityList.objects.count()} Comorbidities already exist. Skipping...")
        return
    # ecl = '<< 35919005'
    # comorbidity_choices = fetch_ecl(ecl)
    comorbidity_choices = (
        fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set()
    )

    for index, comorbidity_choice in enumerate(comorbidity_choices):
        if ComorbidityList.objects.filter(
            conceptId=comorbidity_choice["conceptId"]
        ).exists():
            # duplicate conceptId
            pass
        else:
            new_comorbidity = ComorbidityList(
                conceptId=comorbidity_choice["conceptId"],
                term=comorbidity_choice["term"],
                preferredTerm=comorbidity_choice["preferredTerm"],
            )
            try:
                new_comorbidity.save()
                logger.info(f"{new_comorbidity.preferredTerm} added.")
            except Exception as e:
                logger.info(f"Comorbidity {comorbidity_choice.preferredTerm} not added. {e}")

    # Add 'Other' into ComorbidityList
    ComorbidityList.objects.create(
        conceptId='-1',
        term='Other',
        preferredTerm='Other'
    )
    logger.info(f"Added 'Other' to ComorbidityList.")

    # 'Other' adds one more to list
    logger.info(f"{index+1} comorbidities added")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0008_seed_syndromes"),
    ]

    operations = [migrations.RunPython(seed_comorbidities)]
