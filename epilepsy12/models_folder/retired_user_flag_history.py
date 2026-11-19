from django.db import models


class RetiredUserFlagHistory(models.Model):
    """
    Read-only archive of the retired ``is_rcpch_audit_team_member`` and
    ``is_rcpch_staff`` flags.

    Migration ``0075_remove_rcpch_user_flags`` dropped both fields from
    ``Epilepsy12User`` and its history table. Before dropping them it copied
    the flag values from every ``HistoricalEpilepsy12User`` row here, so the
    complete record of who held them, and when, stays in the platform. One row
    per history row; ``history_id`` links back to it.

    Nothing writes to this table after that migration. Changes to the flags
    were also logged as text in ``VisitActivity.details``.
    """

    history_id = models.IntegerField(
        unique=True,
        help_text="The HistoricalEpilepsy12User row this was copied from.",
    )
    history_date = models.DateTimeField(db_index=True)
    history_type = models.CharField(
        max_length=1, help_text="+ created, ~ changed, - deleted"
    )
    history_user_id = models.BigIntegerField(
        null=True, blank=True, help_text="Id of the user who made the change."
    )
    # Plain ids and copied values rather than foreign keys, so the archive is
    # unaffected if a user is later deleted.
    user_id = models.BigIntegerField(db_index=True)
    email = models.CharField(max_length=254)
    role = models.PositiveSmallIntegerField(null=True, blank=True)
    is_rcpch_audit_team_member = models.BooleanField()
    is_rcpch_staff = models.BooleanField()

    class Meta:
        verbose_name = "Retired RCPCH user flag history"
        verbose_name_plural = "Retired RCPCH user flag history"
        ordering = ["user_id", "history_date"]

    def __str__(self) -> str:
        return f"{self.email} at {self.history_date:%Y-%m-%d %H:%M}"
