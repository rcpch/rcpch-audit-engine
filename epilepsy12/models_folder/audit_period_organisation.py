from django.conf import settings
from django.contrib.gis.db import models

from simple_history.models import HistoricalRecords

from .time_and_user_abstract_base_classes import (
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
)


class AuditPeriodOrganisation(
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
    models.Model,
):
    """
    One approved reporting affiliation per organisation per audit period.

    ``AuditPeriodOrganisation`` records, for a specific ``AuditPeriod`` and
    ``Organisation``:

    - whether the organisation participated in reporting for the audit period
      (``included_in_reporting``); and
    - the Trust / Local Health Board / ICB / NHS England region / OPEN UK
      network / country that applied to that organisation in that audit period.

    The hierarchy FKs are populated by the per-cohort sync from the
    ``rcpch-nhs-organisations`` API ``snapshot`` endpoint at the audit
    period's reference date (``data_collection_end_date``). They are the
    period-aware source of truth for the live dashboard and permission
    services. They are not edited manually except during the approval/review
    workflow, where the audit team may correct a sync-sourced assignment if
    the API data is incomplete or ambiguous.

    Snapshot name fields (``trust_name_snapshot`` etc.) hold the display name
    of each hierarchy entity as it was at the period's reference date. They
    are populated from the same API snapshot response as the FKs and exist
    because the underlying ``Trust`` / ``ICB`` / etc. rows hold only the
    current name (mutated in place by the current-state sync). Historical
    reports read the snapshot name; the live ``Trust`` row continues to hold
    the current name for directory/admin use.

    These snapshot fields are a deliberate interim measure. The expected
    successor is to version the hierarchy entities themselves (``Trust``,
    ``IntegratedCareBoard`` etc.) with ``[valid_from, valid_to)`` intervals
    and repoint these FKs at the specific version row valid for the period.
    At that point the snapshot name fields become redundant and can be
    dropped. They must not be used as identity - the FK is the source of
    truth for which trust/ICB/etc. the organisation belonged to; the
    snapshot name is only the display label.

    See ``documentation/docs/development/audit-period-organisation.md`` for
    the full design, including the access model, the relationship with
    ``OrganisationIdentity``, and the publication snapshot workflow.
    """

    audit_period = models.ForeignKey(
        "epilepsy12.AuditPeriod",
        on_delete=models.PROTECT,
        related_name="organisation_memberships",
        help_text="The audit period this membership applies to.",
    )
    organisation = models.ForeignKey(
        "epilepsy12.Organisation",
        on_delete=models.PROTECT,
        related_name="audit_period_memberships",
        help_text="The organisation this membership is for. Points at the "
        "Organisation row whose ODS code was in use during this audit "
        "period (which may be a predecessor ODS code).",
    )

    included_in_reporting = models.BooleanField(
        default=True,
        help_text="Whether this organisation contributes to reporting for "
        "this audit period. Set to False for organisations that "
        "participated in the audit but are excluded from aggregated "
        "reporting.",
    )

    # --- Hierarchy FKs (period-aware source of truth) ---
    # These are resolved from the API snapshot at the period's reference
    # date. They are PROTECT so that a referenced historical entity (e.g. a
    # dissolved trust) cannot be deleted - it must be retired/marked
    # inactive instead.
    country = models.ForeignKey(
        "epilepsy12.Country",
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
    )
    trust = models.ForeignKey(
        "epilepsy12.Trust",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
        help_text="English trusts. Null for Welsh organisations.",
    )
    local_health_board = models.ForeignKey(
        "epilepsy12.LocalHealthBoard",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
        help_text="Welsh local health boards. Null for English organisations.",
    )
    integrated_care_board = models.ForeignKey(
        "epilepsy12.IntegratedCareBoard",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
    )
    nhs_england_region = models.ForeignKey(
        "epilepsy12.NHSEnglandRegion",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
    )
    openuk_network = models.ForeignKey(
        "epilepsy12.OPENUKNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_period_organisations",
    )

    # --- Snapshot name fields (display labels, interim) ---
    # See class docstring. These hold the name of each hierarchy entity as
    # it was at the period's reference date, for historical display. They
    # are populated from the same API snapshot response as the FKs.
    country_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    trust_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    local_health_board_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    integrated_care_board_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    nhs_england_region_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    openuk_network_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    # --- Approval / provenance ---
    # Sync-sourced rows are candidates until approved by the audit team.
    # Approved rows are not overwritten by re-running the sync. Unapproved
    # rows block publication readiness for the period.
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the audit team approved this membership row. Null "
        "for sync-sourced candidate rows that have not yet been reviewed.",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_audit_period_organisations",
        help_text="The audit-team user who approved this membership row.",
    )
    source = models.CharField(
        max_length=32,
        default="api_snapshot",
        help_text="Provenance of this row. 'api_snapshot' for rows "
        "populated by the per-cohort sync; 'manual' for rows created or "
        "corrected by the audit team.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Free-text notes from the audit team, e.g. reasons for "
        "correcting a sync-sourced assignment.",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Audit period organisation"
        verbose_name_plural = "Audit period organisations"
        constraints = [
            models.UniqueConstraint(
                fields=["audit_period", "organisation"],
                name="unique_organisation_membership_per_audit_period",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.organisation} - {self.audit_period}"
