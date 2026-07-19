from __future__ import annotations
from datetime import date, timedelta
from django.utils import timezone
from django.apps import apps

from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import TimeStampAbstractBaseClass, UserStampAbstractBaseClass
from .entities.organisation import Organisation
from epilepsy12.constants.user_types import CAN_EXTEND_SUBMISSION_DEADLINE
from epilepsy12.constants.audit_period_extension_reasons import AUDIT_PERIOD_EXTENSION_REASONS


from simple_history.models import HistoricalRecords

class AuditPeriodManager(models.Manager):
    def for_first_paediatric_assessment_date(self, fpa_date: date):
        """The period a child recruited on this date belongs to."""
        return self.filter(
            recruitment_start_date__lte=fpa_date,
            recruitment_end_date__gte=fpa_date
        ).first()

    def by_cohort(self, cohort_number: int):
        return self.filter(cohort_number=cohort_number).first()

    def currently_recruiting(self):
        today = timezone.now().date()
        return self.filter(
            recruitment_start_date__lte=today,
            recruitment_end_date__gte=today
        ).first()

    def currently_submitting(self):
        """The cohort closed to recruitment but still completing first-year data."""
        today = timezone.now().date()
        return self.filter(
            recruitment_end_date__lt=today,
            data_collection_end_date__gte=today
        ).first()

    def is_grace_period(self):
        """The cohort is in the grace period after data collection ends."""
        today = timezone.now().date()
        return self.filter(
            data_collection_end_date__lt=today,
            submission_deadline__gte=today
        ).first()

    def most_recently_closed(self):
        """The most recent cohort whose submission deadline has fully passed.

        Used so the dashboard's first cohort card always has a cohort to show
        ("Data submission closed") even when no cohort is currently in grace -
        ``is_grace_period()`` returns None once the deadline has passed.
        """
        today = timezone.now().date()
        return self.filter(submission_deadline__lt=today).order_by(
            "-submission_deadline"
        ).first()

    def visible(self):
        return self.filter(is_visible=True)

    def cohort_summary(self, organisation: Organisation | None = None):
        """
        Returns a dict describing the currently-recruiting, currently-submitting
        and grace-period cohorts, mirroring the shape historically produced by
        ``cohorts_and_dates`` so templates and views can be migrated piecemeal.
        Optional `organisation` parameter to individualise the cohort summary for
        a specific organisation, which may have an extended submission deadline.

        Keys:
            currently_recruiting_cohort          -> int | None
            currently_recruiting_cohort_start_date -> date | None
            currently_recruiting_cohort_end_date   -> date | None
            currently_recruiting_cohort_submission_date -> date | None
            currently_recruiting_cohort_days_remaining -> int | None
            currently_recruiting_cohort_dates     -> dict (card shape) | {}
            submitting_cohort                     -> int | None
            submitting_cohort_start_date          -> date | None
            submitting_cohort_end_date            -> date | None
            submitting_cohort_submission_date      -> date | None
            submitting_cohort_days_remaining      -> int | None
            submitting_cohort_dates               -> dict (card shape) | {}
            grace_cohort                          -> dict (card shape) | {}
            within_grace_period                   -> bool
            today                                 -> date
            organisation                          -> Organisation | None
        """
        today = timezone.now().date()

        recruiting = self.currently_recruiting()
        submitting = self.currently_submitting()
        grace = self.is_grace_period()
        # The first card shows the grace cohort while one is in grace, else the
        # most recently closed cohort, so it is never blank. within_grace_period
        # keeps its strict meaning for callers deciding which cohort is
        # imminently submitting.
        closed_card_period = grace or self.most_recently_closed()

        return {
            "currently_recruiting_cohort": recruiting.cohort_number if recruiting else None,
            "currently_recruiting_cohort_start_date": recruiting.recruitment_start_date if recruiting else None,
            "currently_recruiting_cohort_end_date": recruiting.recruitment_end_date if recruiting else None,
            "currently_recruiting_cohort_submission_date": recruiting.submission_deadline if recruiting else None,
            "currently_recruiting_cohort_days_remaining": recruiting.days_until_submission_deadline_for_organisation(organisation=organisation, current_date=today) if recruiting else None,
            "currently_recruiting_cohort_dates": recruiting.as_cohort_card_dict(today=today, organisation=organisation) if recruiting else {},
            "submitting_cohort": submitting.cohort_number if submitting else None,
            "submitting_cohort_start_date": submitting.recruitment_start_date if submitting else None,
            "submitting_cohort_end_date": submitting.recruitment_end_date if submitting else None,
            "submitting_cohort_submission_date": submitting.submission_deadline if submitting else None,
            "submitting_cohort_days_remaining": submitting.days_until_submission_deadline_for_organisation(organisation=organisation, current_date=today) if submitting else None,
            "submitting_cohort_dates": submitting.as_cohort_card_dict(today=today, organisation=organisation) if submitting else {},
            "grace_cohort": closed_card_period.as_cohort_card_dict(today=today, organisation=organisation) if closed_card_period else {},
            "within_grace_period": grace is not None,
            "today": today,
        }

    def all_cohorts_list(self):
        """
        Return a list of ``{"cohort": int, "has_data": bool}`` for every
        AuditPeriod from the earliest cohort up to the latest cohort that has
        registrations, mirroring the shape historically produced by
        ``get_all_cohort_list``.
        """
        Registration = apps.get_model("epilepsy12", "Registration")
        earliest_cohort = 6

        latest = (
            Registration.objects.filter(audit_period__isnull=False)
            .values("audit_period__cohort_number")
            .order_by("audit_period__cohort_number")
            .last()
        )
        latest_cohort = (
            latest["audit_period__cohort_number"] if latest else earliest_cohort
        )

        return [
            {
                "cohort": cohort,
                "has_data": Registration.objects.filter(
                    audit_period__cohort_number=cohort
                ).exists(),
            }
            for cohort in range(earliest_cohort, latest_cohort + 1)
        ]


class AuditPeriod(
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
    HelpTextMixin,
    models.Model):
    """
       Tracks cohort and cohort dates, submission status, and exposes these as
       slugs for use in URLs and longitudinal reporting.

       submission_date is the single audit-wide deadline: editing it in admin
       extends (or brings forward) submission for the whole audit. Per-site
       extensions are held in AuditPeriodExtension and resolved through
       submission_date_for_organisation().

       A word about cohorts:

           * A cohort number is an `int` calculatefrom the first paediatric assessment date as a Python `datetime.date`

           * Dates which are too early (before onset of cohort 4) to return a valid cohort number will return `None`. Ensure to test for a `None` return value before doing anything with the result.

           * Cohort Number is used to identify the groups in the audit by year.

           * Cohorts are defined between 1st December year and 30th November in the subsequent year. Note, the final submission date
           is the second Tuesday in January after the closing date 1 YEAR ON. So if the cohort closes on 30 Nov 22, the submission date is
           the second Tuesday after 30/11/23, which is 9 Jan 24

           Cohorts are defined as follows:
           currently recruiting cohort: this is the cohort that is currently recruiting patients
           currently submitting cohort: this is the cohort that is no longer recruiting patients but is still collecting data to complete a full year of care
           grace cohort: this cohort is also no longer recruiting patients but is still collecting data to complete a full year of care. This cohort is the one before the submitting cohort.

           For example, if today is in or after December but before the second week of January, there will be three concurrent cohorts:
               - currently recruiting cohort: these children started being recruited on the previous December
               - currently submitting cohort: these children finished being recruited on the previous 30th November and are data are still being collected on them.
               - grace period: these children completed data their full year of care and are waiting for the second week of January to submit their data.

           * Time zone is not explicity supplied. Since this is a UK audit, time zone is assumed always to be UK.

           #### Examples of cohort numbers:
           Cohort 4: 1 December 2020 - 30 November 2021: submission 10 January 2023
           Cohort 5: 1 December 2021 - 30 November 2022: submission 9 January 2024
           Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
           Cohort 7: 1 December 2023 - 30 November 2024: submission 13 January 2026
           Cohort 8: 1 December 2024 - 30 November 2025: submission 12 January 2027
     """

    objects = AuditPeriodManager()

    name = models.CharField(
        blank=True,
        null=True,
        default=None,
        max_length=255,
        help_text={
            "label": "Name",
            "reference": "Optional display name for the audit period.",
        },
    )
    cohort_number = models.PositiveSmallIntegerField(
        help_text={
            "label": "Cohort Number",
            "reference": "The cohort allocated, based on the First Paediatric Assessment date.",
        },
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
    )
    recruitment_start_date = models.DateField(
        help_text={
            "label": "Start Date",
            "reference": "The start date for recruitment to this cohort.",
        },
    )
    recruitment_end_date = models.DateField(
        help_text={
            "label": "End Date",
            "reference": "The end date for recruitment to this cohort.",
        },
    )
    # data collection start date is derived from the recruitment end date
    data_collection_end_date = models.DateField(
        help_text={
            "label": "Data Collection End Date",
            "reference": "The end date for data collection.",
        },
    )
    submission_deadline = models.DateField(
        # Note: this is the audit-wide deadline, not the site-specific end date.
        # Current default is for audit-wide deadline to fall on the 2nd Tuesday of the
        # after the data collection end date (after the grace period)
        help_text={
            "label": "Submission Deadline",
            "reference": "The deadline for submitting data.",
        },
    )
    is_visible = models.BooleanField(
        help_text={
            "label": "Is Visible",
            "reference": "Whether the audit period is visible to the user.",
        },
        default=False,
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ["-recruitment_start_date"]
        verbose_name = "Audit period"
        verbose_name_plural = "Audit periods"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(recruitment_start_date__lt=models.F("recruitment_end_date")),
                name="audit_period_start_date_before_end_date",
            ),
            models.CheckConstraint(
                condition=models.Q(data_collection_end_date__gt=models.F("recruitment_end_date")),
                name="audit_period_data_collection_end_date_after_recruitment_end_date",
            ),
            models.CheckConstraint(
                condition=models.Q(submission_deadline__gt=models.F("data_collection_end_date")),
                name="audit_period_submission_deadline_after_data_collection_end_date",
            ),
        ]

    @property
    def data_collection_start_date(self) -> date:
        # data collection starts the day after the recruitment end date
        return self.recruitment_end_date + timedelta(days=1)

    @property
    def is_recruiting(self) -> bool:
        # returns True if currently recruiting
        return self.recruitment_start_date <= timezone.now().date() <= self.recruitment_end_date

    @property
    def is_collecting_data(self):
        # returns True if currently collecting data
        # Note: data collection ends at the audit-wide deadline, not the site-specific end date
        return self.data_collection_start_date <= timezone.now().date() <= self.data_collection_end_date

    @property
    def is_in_grace_period(self):
        # returns True if currently in the grace period
        # Note: the grace period ends at the audit-wide deadline, not the site-specific end date
        return self.data_collection_end_date < timezone.now().date() <= self.submission_deadline

    @property
    def is_complete(self) -> bool:
        """No data entry possible anywhere, including any per-site extensions."""
        return timezone.now().date() > self.effective_latest_submission_date

    def as_cohort_card_dict(
        self,
        today: date | None = None,
        organisation: Organisation | None = None,
    ) -> dict:
        """
        Returns this AuditPeriod as a dict in the shape consumed by the
        ``cohort_card.html`` template and historically produced by
        ``dates_for_cohort``. ``today`` defaults to today and is used to
        compute ``days_remaining``.
        """
        if today is None:
            today = timezone.now().date()

        extension = self.extensions.filter(organisation=organisation).first() if organisation else None

        return {
            "cohort": self.cohort_number,
            "cohort_start_date": self.recruitment_start_date,
            "cohort_end_date": self.recruitment_end_date,
            "submission_date": self.submission_deadline,
            "days_remaining": self.days_until_submission_deadline_for_organisation(
                organisation=organisation, current_date=today
            ),
            "audit_period_id": self.pk,
            "extended_submission_date": extension.extended_submission_date if extension else None,
            # True when the extension closes submission early (date not after the
            # audit-wide deadline) - the card shows "Closed early" not "Extended to".
            "is_closed_early": (
                extension is not None
                and extension.extended_submission_date <= self.submission_deadline
            ),
            # eligibility is evaluated against the passed-in ``today``, not the
            # is_collecting_data/is_in_grace_period properties, which are pinned
            # to timezone.now(). The window spans data collection start through
            # the audit-wide deadline, covering both submitting and grace.
            "is_extension_eligible": (
                self.data_collection_start_date <= today <= self.submission_deadline
            ),
        }

    # ------------------------------------------------------------------
    # deadline resolution
    # ------------------------------------------------------------------

    @property
    def effective_latest_submission_date(self) -> date:
        """The audit-wide deadline or the latest per-site extension, whichever is later."""
        latest_extension = self.extensions.aggregate(
            latest=models.Max("extended_submission_date")
        )["latest"]
        if latest_extension and latest_extension > self.submission_deadline:
            return latest_extension
        return self.submission_deadline

    def submission_deadline_for_organisation(self, organisation: Organisation) -> date:
        """
        The effective deadline for a given organisation: the audit-wide
        submission_deadline unless this organisation holds an extension row.
        The extension always wins when present — it may be later (a granted
        extension) or earlier (submission closed early by the audit team).
        Falls back to the audit-wide deadline if no organisation is supplied.
        """
        if organisation is None:
            return self.submission_deadline
        extension = self.extensions.filter(organisation=organisation).first()
        if extension:
            return extension.extended_submission_date
        return self.submission_deadline

    def days_until_submission_deadline_for_organisation(
        self, organisation: Organisation | None, current_date: date | None = None
    ) -> int:
        """
        Returns the number of days until the effective submission deadline for a
        given organisation, honouring any per-site extension.
        Inclusive of the deadline day itself (submission is possible on the last
        day), clamped at zero once the deadline has passed.
        """
        if current_date is None:
            current_date = timezone.now().date()
        deadline = self.submission_deadline_for_organisation(organisation)
        return max(0, (deadline - current_date).days + 1)

    def extend_submission_deadline(
        self, organisation: Organisation, days: int, user, reason: int = None
    ) -> AuditPeriodExtension:
        """
        Grant (or further extend) this organisation's submission deadline by
        ``days`` beyond its current effective deadline. One row per organisation
        per period; the existing row is edited in place on re-extension.
        """
        today = timezone.now().date()
        if not (self.data_collection_start_date <= today <= self.submission_deadline):
            raise ValidationError(
                "Extensions can only be granted for the submitting or grace cohort."
            )

        extended_deadline = self.submission_deadline_for_organisation(organisation) + timedelta(days=days)
        if extended_deadline <= self.submission_deadline:
            raise ValidationError(
                "Extended date must be after the audit-wide submission deadline."
            )

        valid_reasons = {code for code, _label in AUDIT_PERIOD_EXTENSION_REASONS}
        if reason is not None and reason not in valid_reasons:
            raise ValidationError("Invalid reason for extension.")


        extension, created = self.extensions.update_or_create(
            organisation=organisation,
            defaults={
                "extended_submission_date": extended_deadline,
                "reason": reason,
                "updated_by": user,
            },
        )
        if created:
            extension.created_by = user
            extension.save(update_fields=["created_by"])
        return extension

    def close_submission_for_organisation(
        self, organisation: Organisation, user
    ) -> "AuditPeriodExtension":
        """
        Close this organisation's submission immediately: the extension row's
        date is set to today (inclusive — submission is still possible today).
        No reason is required. Same eligibility window as granting an extension.
        """
        today = timezone.now().date()
        if not (self.data_collection_start_date <= today <= self.submission_deadline):
            raise ValidationError(
                "Submission can only be closed early for the submitting or grace cohort."
            )

        extension, created = self.extensions.update_or_create(
            organisation=organisation,
            defaults={
                "extended_submission_date": today,
                "reason": None,
                "updated_by": user,
            },
        )
        if created:
            extension.created_by = user
            extension.save(update_fields=["created_by"])
        return extension

    def remove_submission_extension(self, organisation: Organisation, user) -> None:
        """
        Remove this organisation's extension, reverting to the audit-wide
        deadline. Refused once the audit-wide deadline has passed — the row is
        then historical record of the deadline the organisation submitted against.
        """
        today = timezone.now().date()
        if today > self.submission_deadline:
            raise ValidationError(
                "Extensions cannot be removed after the audit-wide submission deadline has passed."
            )

        extension = self.extensions.filter(organisation=organisation).first()
        if extension is None:
            raise ValidationError("This organisation has no extension to remove.")

        # stamp who removed it before deleting so the history record keeps the actor
        extension.updated_by = user
        extension.save(update_fields=["updated_by"])
        extension.delete()

    def clean(self):
        if self.recruitment_end_date <= self.recruitment_start_date:
            raise ValidationError("Recruitment end date must be after recruitment start date")
        if self.data_collection_end_date < self.recruitment_end_date:
            raise ValidationError("Data collection end date must be after recruitment end date")
        if self.submission_deadline < self.data_collection_end_date:
            raise ValidationError("Submission deadline must be after data collection end date")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) if self.name else f"cohort-{self.cohort_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Cohort {self.cohort_number}"
            f" ({self.recruitment_start_date} to {self.recruitment_end_date})"
        )

class AuditPeriodExtension(
    TimeStampAbstractBaseClass,
    UserStampAbstractBaseClass,
    models.Model
):
    """
    Grants a single organisation a later submission deadline for one audit period.
    Created/edited by RCPCH audit team in admin. One extension per organisation
    per period; edit the row to extend further.
    """

    audit_period = models.ForeignKey(
        AuditPeriod,
        on_delete=models.CASCADE,
        related_name="extensions"
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="audit_period_extensions"
    )

    extended_submission_date = models.DateField()
    reason = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=AUDIT_PERIOD_EXTENSION_REASONS
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Audit Period site extension"
        verbose_name_plural = "Audit Period site extensions"
        constraints = [
            models.UniqueConstraint(
                fields=["audit_period", "organisation"],
                name="one_extension_per_organisation_per_audit_period"
            )
        ]
        permissions = [
            CAN_EXTEND_SUBMISSION_DEADLINE
        ]

    def clean(self):
        # Note: the date may legitimately be earlier than the audit-wide
        # deadline - that is how the audit team closes an organisation's
        # submission early. Sanity floor: never before data collection starts.
        if (
            self.audit_period_id
            and self.extended_submission_date
            and self.extended_submission_date < self.audit_period.data_collection_start_date
        ):
            raise ValidationError(
                "Extended submission date cannot be before data collection starts."
            )

    def __str__(self):
        return f"{self.organisation} extension granted to {self.extended_submission_date}"
