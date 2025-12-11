from django.apps import apps


def get_medicine_choices(management, antiepilepsy_medicine_id=None, is_rescue=False):
    """
    Returns list of comorbidities to populate dropdown lists
    Removes any items that have already been selected
    Accepts a multiaxial diagnosis instance
    """

    AntiEpilepsyMedicine = apps.get_model("epilepsy12", "AntiEpilepsyMedicine")
    Medicine = apps.get_model("epilepsy12", "Medicine")

    # Get all comorbidity entities that have been selected for this multiaxial diagnosis except the current one
    all_selected_medicines = (
        AntiEpilepsyMedicine.objects.filter(management=management)
        .filter(
            antiepilepsy_medicine_stop_date__isnull=True
        )  # only exclude active medicines
        .exclude(pk=antiepilepsy_medicine_id)
        .values_list("medicine_entity", flat=True)
    )

    # Filter out None values from all_selected_medicines
    all_selected_medicineentities = [
        entity for entity in all_selected_medicines if entity is not None
    ]

    medicine_choices = (
        Medicine.objects.filter(is_rescue=is_rescue)
        .exclude(pk__in=all_selected_medicineentities)
        .order_by("preferredTerm")
    )

    return medicine_choices
