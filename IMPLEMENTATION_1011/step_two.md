## Step 2

1. At this point, each `Epilepsy12User` record will still be associated with an organisation through the `organisation_employer` field. We therefore need to copy the relationship from that field to the new table. This is done with a new custom migration.
    `python manage.py makemigrations --emply epilepsy12 migrate_users_to_organisation_employer`
2. This creates an empty file in the migrations folder

   ```python
    from django.db import migrations

    def migrate_existing_data(apps, schema_editor):
        Epilepsy12User = apps.get_model("epilepsy12", "Epilepsy12User")
        OrganisationEmployer = apps.get_model("epilepsy12", "OrganisationEmployer")

        for user in Epilepsy12User.objects.all():
            if user.organisation_employer:
                OrganisationEmployer.objects.create(
                    epilepsy12user=user,
                    organisation=user.organisation_employer,
                    is_primary=True,
                    is_active=True,
                    join_date=user.date_joined,
                    deactivation_date=None
                )


    class Migration(migrations.Migration):

        dependencies = [
            (
                "epilepsy12",
                "0032_remove_epilepsy12user_organisation_employer_and_more",
            ),  # Replace with the actual previous migration name
        ]

        operations = [
            migrations.RunPython(migrate_existing_data),
        ]
   ```

3. This file needs pushing to live which will trigger `python manage.py makemigrations` and `python manage.py makemigrations migrate`
4. We must then check in the admin that users have the same organisation affiliation in the `Epilepsy12User` model in the `organisation_employer` field and  in the related `EmployerOrganisation`
5. It is possibly worth running a custom test, either to call from the command line through `manage.py` or `pytest` to ensure that all users have two matching fields and values as above. **This needs writing**.
