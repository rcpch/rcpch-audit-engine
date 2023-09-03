# Django imports
from django.db import migrations

from ..constants import TRUSTS


def seed_trusts(apps, schema_editor):
    """
    Seed function which populates the Trust table from JSON and links to BoundaryEntity table.
    Also links all items of the LocalHealthBoard table to the BoundaryEntity model
    By the end of this function, the 7 LocalHealthBoard records should have a corresponding record in BoundaryEntity
    By the end of this function, the 138 Trust records should have a corresponding record in BoundaryEntity
    All 235 records will be associated with a country
    """

    # Get models
    Trust = apps.get_model("epilepsy12", "Trust")

    if Trust.objects.all().count == 242:
        print("\033[31m", "242 Trusts already seeded. Skipping...", "\033[31m")
    else:
        print("\033[31m", "Adding new Trusts...", "\033[31m")

        for added, trust in enumerate(TRUSTS):
            try:
                Trust.objects.create(
                    ods_code=trust["ods_code"],
                    trust_name=trust["trust_name"],
                    address_line_1=trust["address_line_1"],
                    address_line_2=trust.get("address_line_2"),
                    town=trust["town"],
                    postcode=trust["postcode"],
                    country=trust["country"],
                ).save()
                print(f"{added+1}: {trust['trust_name']}")
            except Exception as error:
                print(f"Unable to save {trust['trust_name']}: {error}")

        print(f"{added+1} trusts added.")


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0003_ods_codes_to_abstraction_levels"),
    ]

    operations = [migrations.RunPython(seed_trusts)]
