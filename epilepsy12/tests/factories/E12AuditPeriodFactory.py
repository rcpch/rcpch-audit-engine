"""Factory fn to create new E12 AuditPeriods"""

# standard imports
from datetime import date

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import AuditPeriod


class E12AuditPeriodFactory(factory.django.DjangoModelFactory):
    """Factory for AuditPeriod.

    Tests usually pass ``registration__audit_period__cohort_number=N`` to
    ``e12_case_factory``. Rather than creating a new row each time (which would
    violate the unique constraint on cohort_number), this factory delegates to
    ``AuditPeriod.objects.get_or_create`` so the seeded rows are reused.
    """

    class Meta:
        model = AuditPeriod
        django_get_or_create = ("cohort_number",)

    cohort_number = 6
    name = ""
    recruitment_start_date = date(2022, 12, 1)
    recruitment_end_date = date(2023, 11, 30)
    data_collection_end_date = date(2024, 11, 30)
    submission_deadline = date(2025, 1, 14)
    is_visible = False
