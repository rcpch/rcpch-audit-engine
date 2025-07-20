# django
from django.contrib.gis.db import models
from django.utils import timezone


class VisitActivity(models.Model):
    SUCCESSFUL_LOGIN = 1
    UNSUCCESSFUL_LOGIN = 2
    LOGOUT = 3
    PASSWORD_RESET_LINK_SENT = 4
    PASSWORD_RESET = 5
    SETUP_TWO_FACTOR_AUTHENTICATION = 6
    PASSWORD_LOCKOUT = 7
    UPLOADED_CSV = 8
    TOUCHED_PATIENT_RECORD = 9  # This is not implemented yet
    CREATED_USER_RECORD = 10
    CHANGED_USER_RECORD = 11
    CHANGED_USER_ROLE = 12
    CHANGED_ADMIN_FLAG = 13
    DELETED_USER_RECORD = 14
    ASSIGNED_USER_TO_EMPLOYER = 15
    REMOVED_USER_FROM_EMPLOYER = 16
    USER_EMPLOYER_ROLE_CHANGED = 17

    ACTIVITY = (
        (SUCCESSFUL_LOGIN, "Successful login"),
        (UNSUCCESSFUL_LOGIN, "Login failed"),
        (LOGOUT, "Logout"),
        (PASSWORD_RESET_LINK_SENT, "Password reset link sent"),
        (PASSWORD_RESET, "Password reset successfully"),
        (PASSWORD_LOCKOUT, "Password lockout"),
        (SETUP_TWO_FACTOR_AUTHENTICATION, "Two factor authentication set up"),
        (UPLOADED_CSV, "Uploaded CSV"),
        (
            TOUCHED_PATIENT_RECORD,
            "Touched patient record",
        ),  #  - This is not implemented yet
        (CREATED_USER_RECORD, "Created a user record"),
        (CHANGED_USER_RECORD, "User record changed"),
        (CHANGED_USER_ROLE, "User role changed"),
        (CHANGED_ADMIN_FLAG, "Superuser or admin status changed"),
        (DELETED_USER_RECORD, "User record deleted"),
        (ASSIGNED_USER_TO_EMPLOYER, "User assigned to employer"),
        (REMOVED_USER_FROM_EMPLOYER, "User removed from employer"),
        (USER_EMPLOYER_ROLE_CHANGED, "User employer role changed"),
    )

    activity_datetime = models.DateTimeField(auto_created=True, default=timezone.now)

    activity = models.PositiveSmallIntegerField(choices=ACTIVITY, default=1)

    ip_address = models.CharField(max_length=250, blank=True, null=True)

    epilepsy12user = models.ForeignKey(
        "epilepsy12.Epilepsy12User", on_delete=models.CASCADE
    )

    epilepsy12user_admin = models.ForeignKey(
        "epilepsy12.Epilepsy12User",
        on_delete=models.CASCADE,
        related_name="admin_activity",
        blank=True,
        null=True,
        help_text="The user with admin permissions responsible for the activity, if applicable.",
    )

    details = models.TextField(
        blank=True,
        null=True,
        help_text="Details of the activity, such as the reason for a password reset or the type of CSV uploaded.",
    )

    class Meta:
        indexes = [models.Index(fields=["activity_datetime"])]
        verbose_name = "VisitActivity"
        verbose_name_plural = "VisitActivities"
        ordering = ("activity_datetime",)

    def __str__(self) -> str:
        return f"{self.epilepsy12user} on {self.activity_datetime}"
