import os

from django.apps import apps
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from ...constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_ADMINISTRATOR,
    RCPCH_AUDIT_TEAM
)

class Command(BaseCommand):
    help = "Create test users using the base set in environment variables: LOCAL_DEV_ADMIN_EMAIL and LOCAL_DEV_ADMIN_PASSWORD."

    def create_user_if_not_exists(self, email, first_name, surname, password, role):
        user_model = get_user_model()

        if not user_model.objects.filter(email=email).exists():
            Organisation = apps.get_model("epilepsy12", "Organisation")

            dev_organisation_employer = Organisation.objects.get(
                ods_code="8HV48"  # RCPCH
            )

            user_model.objects.create_user(
                first_name=first_name,
                surname=surname,
                email=email,
                password=password,
                role=role,
                is_active=True,
                organisation_employer=dev_organisation_employer,
                email_confirmed=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created {email}."))
        else:
            self.stdout.write(self.style.WARNING(f"{email} already exists."))

    def handle(self, *args, **kwargs):
        user_model = get_user_model()

        # Grab environment variables
        local_dev_admin_email = os.environ.get("LOCAL_DEV_ADMIN_EMAIL", None)
        password = os.environ.get("LOCAL_DEV_ADMIN_PASSWORD", None)

        if not local_dev_admin_email or not password:
            self.stdout.write(self.style.WARNING("LOCAL_DEV_ADMIN_EMAIL or LOCAL_DEV_ADMIN_PASSWORD not set. Not creating any test users."))

        (local_part, domain) = local_dev_admin_email.split("@")

        lead_clinician_dev_email = f"{local_part}+lead_clinician@{domain}"
        clinician_dev_email = f"{local_part}+clinician@{domain}"
        administrator_dev_email = f"{local_part}+administrator@{domain}"

        if not user_model.objects.filter(email=local_dev_admin_email).exists():
            Organisation = apps.get_model("epilepsy12", "Organisation")

            dev_organisation_employer = Organisation.objects.get(
                ods_code="8HV48"  # RCPCH
            )

            user_model.objects.create_superuser(
                first_name="Superuser",
                surname="DevUser",
                email=local_dev_admin_email,
                password=password,
                role=RCPCH_AUDIT_TEAM,
                organisation_employer=dev_organisation_employer
            )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created {local_dev_admin_email}."))
        else:
            self.stdout.write(self.style.WARNING(f"{local_dev_admin_email} already exists."))

        self.create_user_if_not_exists(
            email=lead_clinician_dev_email,
            first_name="LeadClinician",
            surname="DevUser",
            password=password,
            role=AUDIT_CENTRE_LEAD_CLINICIAN,
        )

        self.create_user_if_not_exists(
            email=clinician_dev_email,
            first_name="Clinician",
            surname="DevUser",
            password=password,
            role=AUDIT_CENTRE_CLINICIAN,
        )

        self.create_user_if_not_exists(
            email=administrator_dev_email,
            first_name="Administrator",
            surname="DevUser",
            password=password,
            role=AUDIT_CENTRE_ADMINISTRATOR,
        )
        

