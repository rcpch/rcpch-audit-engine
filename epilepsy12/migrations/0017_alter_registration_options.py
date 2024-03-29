# Generated by Django 4.2.7 on 2023-11-18 13:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0016_alter_site_transfer_origin_organisation"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="registration",
            options={
                "permissions": [
                    (
                        "can_approve_eligibility",
                        "Can approve eligibility for Epilepsy12.",
                    ),
                    (
                        "can_register_child_in_epilepsy12",
                        "Can register child in Epilepsy12. (A cohort number is automatically allocated)",
                    ),
                    (
                        "can_unregister_child_in_epilepsy12",
                        "Can unregister a child in Epilepsy. Their record and previously entered data is untouched.",
                    ),
                    (
                        "can_consent_to_audit_participation",
                        "Can consent to participating in Epilepsy12.",
                    ),
                ],
                "verbose_name": "Registration",
                "verbose_name_plural": "Registrations",
            },
        ),
    ]
