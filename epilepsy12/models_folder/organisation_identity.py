from django.contrib.gis.db import models

from simple_history.models import HistoricalRecords

from .time_and_user_abstract_base_classes import (
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
)


class OrganisationIdentity(
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
    models.Model,
):
    """
    The stable identity of a physical hospital, independent of ODS code.

    One row per hospital, ever. Does not change when trusts merge or ODS
    codes change. Used to link successive ``Organisation`` rows that
    represent the same physical hospital across code changes.

    A hospital's ODS code can change when its parent trust is dissolved and
    its services are redistributed (for example Princess Royal University
    Hospital changed from ``RYQ30`` to ``RJZ30`` in 2013). This can happen
    more than once, so the design must handle arbitrary-length succession
    chains (``RYQ30`` -> ``RJZ30`` -> ``RXZ40``). ``OrganisationIdentity``
    groups all the ``Organisation`` rows for the same hospital into a single
    identity, so the full set of ODS codes for a hospital is available in a
    single query:

        Organisation.objects.filter(identity=hospital_identity)

    This matters for:

    - **Longitudinal reporting** - following a hospital's results across ODS
      code changes between audit periods.
    - **User access** - a clinician employed at the current ODS code
      (``RJZ30``) needs access to cases stored against the predecessor ODS
      code (``RYQ30``). Resolving this via ``identity`` is a single join.
    - **Case visibility** - ``Site.organisation`` may point at a predecessor
      ``Organisation`` row. The clinician's access is resolved by checking
      whether their employer's ``Organisation`` shares the same
      ``OrganisationIdentity``.

    ``OrganisationIdentity`` is a grouping layer above ``Organisation``, not
    a replacement for it. It is populated by the per-cohort sync when the
    API's succession data indicates that two ODS codes represent the same
    physical hospital. It does not carry names or other mutable attributes -
    those belong to the period-aware layer (``AuditPeriodOrganisation``) or
    the entity layer (``Organisation`` / ``Trust``).
    """

    name = models.CharField(
        max_length=255,
        help_text="Current display name for the hospital. Used for admin and "
        "debugging only; historical reporting reads period-specific names "
        "from AuditPeriodOrganisation.",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Organisation identity"
        verbose_name_plural = "Organisation identities"

    def __str__(self) -> str:
        return self.name
