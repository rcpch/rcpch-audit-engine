# """
# This file contains signals that are triggered when:
#  - a user logs in, logs out, or fails to log in. (Stored in the VisitActivity model)
#  - a user sets up two-factor authentication (Stored in the VisitActivity model)
#  - a user is created
#  - a user changes their role
#  - a user changes their group membership
#  - a user changes their employer
#  Particularly sensitive fields are logged and trigger email notifications.
# """

# python imports
import logging

# django imports
from django.apps import apps
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

# third party
from two_factor.signals import user_verified

# RCPCH
from .general_functions.email import send_email_to_recipients
from .general_functions.client_ip import get_client_ip
from .models import VisitActivity, Epilepsy12User, OrganisationEmployer
from django.conf import settings

# Logging setup
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"{user} ({user.email}) logged in from {get_client_ip(request)}.")
    VisitActivity.objects.create(
        activity=1, ip_address=get_client_ip(request), epilepsy12user=user
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, request, user=None, **kwargs):
    if user is not None:
        VisitActivity.objects.create(
            activity=2, ip_address=get_client_ip(request), epilepsy12user=user
        )
        logger.info(
            f"{user} ({user.email}) failed log in from {get_client_ip(request)}."
        )
    elif "credentials" in kwargs:
        if Epilepsy12User.objects.filter(
            email=kwargs["credentials"]["username"]
        ).exists():
            user = Epilepsy12User.objects.get(email=kwargs["credentials"]["username"])
            VisitActivity.objects.create(
                activity=2, ip_address=get_client_ip(request), epilepsy12user=user
            )
            logger.info(
                f"{user} ({user.email}) failed log in from {get_client_ip(request)}."
            )
        else:
            logger.info("Login failure by unknown user")
    else:
        logger.info("Login failure by unknown user")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        logger.info(f"{user} ({user.email}) logged out from {get_client_ip(request)}.")
        VisitActivity.objects.create(
            activity=3, ip_address=get_client_ip(request), epilepsy12user=user
        )
    else:
        logger.info(f"Anonymous user logged out from {get_client_ip(request)}.")


# Epilepsy12User Signal handlers
@receiver(pre_save, sender=Epilepsy12User)
def set_updated_by(sender, instance, **kwargs):
    from epilepsy12.middleware import get_current_user

    current_user = get_current_user()
    if instance.pk:
        logger.info(f"{instance} ({instance.email}) updated by {current_user}.")
        instance.updated_by = current_user


@receiver(post_save, sender=Epilepsy12User)
def set_created_by(sender, instance, created, **kwargs):
    from epilepsy12.middleware import get_current_user

    current_user = get_current_user()
    if created:
        instance.created_by = current_user
        instance.save()
        logger.info(f"{instance} ({instance.email}) created by {instance.updated_by}.")


# Two factor auth receiver
@receiver(user_verified)
def two_factor_auth_setup(request, user, device, **kwargs):
    if (
        user_verified
        and VisitActivity.objects.filter(epilepsy12user=user, activity=6).count() < 1
    ):
        logger.info(
            f"{user} ({user.email}) has logged in the for the first time with two factor authentication."
        )
        VisitActivity.objects.create(
            activity=6, ip_address=get_client_ip(request), epilepsy12user=user
        )


# Fields that should trigger email notifications when changed
EMAIL_TRIGGER_FIELDS = [
    "is_superuser",
    "is_rcpch_audit_team_member",
    "is_rcpch_staff",
    "is_superuser",
    "is_staff",
    "email",
    "is_active",
]

# Fields that should be logged when changed
LOGGED_FIELDS = [
    "role",
    "is_active",
    "is_rcpch_audit_team_member",
    "is_rcpch_staff",
    "is_staff",
    "email",
    "first_name",
    "surname",
]

ACTIVITY = (
    (1, "Successful login"),  # SUCCESSFUL_LOGIN
    (2, "Login failed"),  # UNSUCCESSFUL_LOGIN
    (3, "Logout"),  # LOGOUT
    (4, "Password reset link sent"),  # PASSWORD_RESET_LINK_SENT
    (5, "Password reset successfully"),  # PASSWORD_RESET
    (6, "Password lockout"),  # PASSWORD_LOCKOUT
    (7, "Two factor authentication set up"),  # SETUP_TWO_FACTOR_AUTHENTICATION
    (8, "Uploaded CSV"),  # UPLOADED_CSV
    (
        9,
        "Touched patient record",
    ),  #  - This is not implemented yet # TOUCHED_PATIENT_RECORD
    (10, "Created a user record"),  # CREATED_USER_RECORD
    (11, "User record changed"),  # CHANGED_USER_RECORD
    (12, "User role changed"),  # CHANGED_USER_ROLE
    (13, "Superuser or admin status changed"),  # CHANGED_ADMIN_FLAG
    (14, "User record deleted"),  # DELETED_USER_RECORD
    (15, "User assigned to Employer"),  # ASSIGNED_USER_TO_EMPLOYER
    (16, "User removed from Employer"),  # REMOVED_USER_FROM_EMPLOYER
    (17, "User Employer role changed"),  # USER_EMPLOYER_ROLE_CHANGED
)


@receiver(pre_save, sender=Epilepsy12User)
def capture_user_changes(sender, instance, **kwargs):
    """
    Capture the original state before save to compare changes.
    """
    if instance.pk:  # Only for existing users (updates)
        try:
            # Store original values for comparison
            original = Epilepsy12User.objects.get(pk=instance.pk)
            instance._original_values = {
                field: getattr(original, field) for field in LOGGED_FIELDS
            }
        except Epilepsy12User.DoesNotExist:
            instance._original_values = {}
    else:
        # New user creation
        instance._original_values = {}


@receiver(post_save, sender=Epilepsy12User)
def log_and_notify_user_changes(sender, instance, created, **kwargs):
    """
    Log changes and send notifications after user is saved.
    """
    from .middleware import get_current_user

    current_user = get_current_user()

    if created:
        # Log user creation
        _log_user_activity(
            user=instance,
            activity_type=10,  # CREATED_USER_RECORD
            details=f"User created by {current_user.email if current_user else 'system'}",
            current_user=current_user,
        )

        # Send email notification to admins
        _send_user_creation_notification(instance, current_user)

    else:
        # Handle user updates
        original_values = getattr(instance, "_original_values", {})
        if original_values:
            changes = _detect_changes(instance, original_values)

            if changes:
                # Log all changes
                _log_user_changes(instance, changes, current_user)

                # Send email notifications for critical changes
                _send_change_notifications(instance, changes, current_user)


@receiver(post_save, sender=OrganisationEmployer)
def log_user_organisation_assignment(sender, instance, created, **kwargs):
    """
    Log when a user is assigned to or updated an employer.
    """
    from .middleware import get_current_user

    current_user = get_current_user()

    if created:
        # Log new OrganisationEmployer creation
        details = f"User {instance.epilepsy12_user.email} assigned to Organisation {instance.employer_organisation}  by {current_user.email if current_user else 'system'}"

        _log_user_activity(
            user=instance.epilepsy12_user,
            activity_type=15,  # USER_ASSIGNED_TO_ORGANISATION
            details=details,
            current_user=current_user,
        )

        #         # Send notification to admins about new Employer assignment
        _send_employer_assignment_notification(instance, current_user, is_new=True)

        logger.info(
            f"User {instance.epilepsy12_user.email} assigned to employer {instance.employer_organisation} ({instance.employer_organisation.trust}) by {current_user.email if current_user else 'system'}"
        )
    else:
        # Employer assignment updated (is_primary change, etc.)
        details = f"Employer assignment updated for user {instance.epilepsy12_user.email} at employer {instance.employer_organisation} by {current_user.email if current_user else 'system'}"

        _log_user_activity(
            user=instance.epilepsy12_user,
            activity_type=17,  # EMPLOYER_ROLE_CHANGED
            details=details,
            current_user=current_user,
        )

        logger.info(
            f"Employer assignment updated for user {instance.epilepsy12_user.email} at employer {instance.employer_organisation} ({instance.employer_organisation.trust})"
        )


@receiver(pre_delete, sender=OrganisationEmployer)
def log_user_employer_removal(sender, instance, **kwargs):
    """
    Log when a user is removed from an employer.
    """
    from .middleware import get_current_user

    current_user = get_current_user()

    details = f"User {instance.epilepsy12_user.email} removed from employer {instance.employer_organisation} by {current_user.email if current_user else 'system'}"

    _log_user_activity(
        user=instance.epilepsy12_user,
        activity_type=16,  # REMOVED_USER_FROM_EMPLOYER
        details=details,
        current_user=current_user,
    )

    # Send notification to admins about employer removal
    _send_employer_assignment_notification(
        instance, current_user, is_new=False, is_removal=True
    )

    logger.info(details)


@receiver(pre_save, sender=OrganisationEmployer)
def capture_employer_assignment_changes(sender, instance, **kwargs):
    """
    Capture the original state before save to compare changes.
    """
    OrganisationEmployer = apps.get_model("epilepsy12", "OrganisationEmployer")
    if instance.pk:  # Only for existing assignments (updates)
        try:
            original = OrganisationEmployer.objects.get(pk=instance.pk)
            instance._original_values = {
                "employer_organisation": original.employer_organisation,
                "epilepsy12_user": original.epilepsy12_user,
                "is_primary": getattr(original, "is_primary", None),
            }
        except OrganisationEmployer.DoesNotExist:
            instance._original_values = {}
    else:
        instance._original_values = {}


"""
Helper functions
"""


def _detect_changes(instance, original_values):
    """
    Compare current instance with original values to detect changes.
    """
    changes = {}

    for field in LOGGED_FIELDS:
        original_value = original_values.get(field)
        current_value = getattr(instance, field)

        if original_value != current_value:
            changes[field] = {"old": original_value, "new": current_value}

    return changes


def _log_user_activity(user, activity_type, details, current_user=None):
    """
    Create a log entry for user activity and store it in VisitActivity as well as logging it.
    """
    try:
        from .middleware import get_current_request

        current_request = get_current_request()

        ip_address = get_client_ip(current_request) if current_request else None

        VisitActivity.objects.create(
            activity=activity_type,
            ip_address=ip_address,
            epilepsy12user=user,
            epilepsy12user_admin=current_user,
            details=details,
        )
    except Exception as e:
        logging.error(f"Failed to log user activity for {user.email}: {e}")
        return

    activity_type_name = dict(ACTIVITY).get(activity_type, "Unknown activity")
    logging.info(
        f"Logging user activity: {activity_type_name} for user {user.email}: {details}. Current user: {current_user.email if current_user else 'system'}"
    )


def _log_user_changes(user, changes, current_user):
    """
    Log specific field changes for a user.
    """
    change_details = []

    for field, change in changes.items():
        change_detail = f"{field}: '{change['old']}' → '{change['new']}'"
        change_details.append(change_detail)

    details = f"User updated by {current_user.email if current_user else 'system'}: {'; '.join(change_details)}"

    activity_type = _map_changes_to_visit_activity(changes)

    _log_user_activity(
        user=user,
        activity_type=activity_type,
        details=details,
        current_user=current_user,
    )


def _send_change_notifications(user, changes, current_user):
    """
    Send email notifications for critical field changes.
    """
    email_worthy_changes = {
        field: change
        for field, change in changes.items()
        if field in EMAIL_TRIGGER_FIELDS
    }

    if not email_worthy_changes:
        return

    # Send notification to user if email changed
    if "email" in email_worthy_changes:
        _send_email_change_notification(
            user, email_worthy_changes["email"], current_user
        )

    # Send notification to admins for role/permission changes
    role_permission_changes = {
        field: change
        for field, change in email_worthy_changes.items()
        if field
        in ["role", "is_rcpch_audit_team_member", "is_rcpch_staff", "is_active"]
    }

    if role_permission_changes:
        _send_admin_notification(user, role_permission_changes, current_user)


def _send_email_change_notification(user, email_change, current_user):
    """
    Notify user when their email address is changed.
    """
    old_email = email_change["old"]
    new_email = email_change["new"]

    subject = "E12 user Account Email Address Changed"
    message = f"""
    Your E12 user account email address has been changed.

    Previous email: {old_email}
    New email: {new_email}
    Changed by: {current_user.email if current_user else 'System'}

    If you did not request this change, please contact the NPDA team immediately.
    """

    # Send to both old and new email addresses
    recipients = [old_email, new_email] if old_email != new_email else [new_email]

    try:
        send_email_to_recipients(
            recipients=recipients, subject=subject, message=message
        )
        logger.info(f"Email change notification sent for user {user.email}")
    except Exception as e:
        logger.error(
            f"Failed to send email change notification for user {user.email}: {e}"
        )


def _send_admin_notification(user, changes, current_user):
    """
    Send notification to admins when user roles/permissions change.
    """
    change_details = []
    for field, change in changes.items():
        change_details.append(f"{field}: '{change['old']}' → '{change['new']}'")

    subject = f"E12 User Permission Changes - {user.get_full_name()}"
    message = f"""
    User permissions have been modified:

    User: {user.get_full_name()} ({user.email})
    Changed by: {current_user.email if current_user else 'System'}

    Changes:
    {chr(10).join(f'• {detail}' for detail in change_details)}
    """
    # send to admins
    try:
        if settings.USER_CHANGE_NOTIFICATION_EMAILS:
            send_email_to_recipients(
                recipients=settings.USER_CHANGE_NOTIFICATION_EMAILS, subject=subject, message=message
            )
            logger.info(f"Admin notification sent for user changes: {user.email}")
    except Exception as e:
        logger.error(f"Failed to send admin notification for user {user.email}: {e}")


def _send_user_creation_notification(user, current_user):
    """
    Send notification when new user is created.
    """
    subject = f"New E12 User Created - {user.get_full_name()}"
    message = f"""
    A new E12 user has been created:

    User: {user.get_full_name()} ({user.email})
    Role: {user.get_role_display()}
    Created by: {current_user.email if current_user else 'System'}
    """

    # Send to audit team members
    try:
        if settings.CHANGE_NOTIFICATION_EMAILS:
            send_email_to_recipients(
                recipients=settings.CHANGE_NOTIFICATION_EMAILS, subject=subject, message=message
            )
            logger.info(f"User creation notification sent for: {user.email}")
    except Exception as e:
        logger.error(f"Failed to send user creation notification for {user.email}: {e}")


def _map_changes_to_visit_activity(changes):
    """
    Map changes to VisitActivity activity codes.
    ACTIVITY = (
        (SUCCESSFUL_LOGIN, "Successful login"),
        (UNSUCCESSFUL_LOGIN, "Login failed"),
        (LOGOUT, "Logout"),
        (PASSWORD_RESET_LINK_SENT, "Password reset link sent"),
        (PASSWORD_RESET, "Password reset successfully"),
        (PASSWORD_LOCKOUT, "Password lockout"),
        (SETUP_TWO_FACTOR_AUTHENTICATION, "Two factor authentication set up"),
        (UPLOADED_CSV, "Uploaded CSV"),
        (TOUCHED_PATIENT_RECORD, "Touched patient record"), #  - This is not implemented yet
        (CREATED_USER_RECORD, "Created a user record"),
        (CHANGED_USER_RECORD, "User record changed"),
        (CHANGED_USER_ROLE, "User role changed"),
        (CHANGED_ADMIN_FLAG, "Superuser or admin status changed"),
        (DELETED_USER_RECORD, "User record deleted"), # 14
        (ASSIGNED_USER_TO_EMPLOYER, "User assigned to employer"),      # 15
        (REMOVED_USER_FROM_EMPLOYER, "User removed from employer"),     # 16
        (USER_EMPLOYER_ROLE_CHANGED, "User employer role changed"),     # 17
    )
    """

    ADMIN_FLAGS = ["is_active", "is_rcpch_audit_team_member", "is_rcpch_staff"]
    USER_RECORD_FIELDS = ["email", "first_name", "surname"]

    if "role" in changes:
        return 12  # CHANGED_USER_ROLE
    elif any(field in changes for field in ADMIN_FLAGS):
        return 13  # CHANGED_ADMIN_FLAG
    elif any(field in changes for field in USER_RECORD_FIELDS):
        return 11  # CHANGED_USER_RECORD
    else:
        # Default to a generic user update activity
        return 11


def _send_employer_assignment_notification(
    organisation_employer_instance, current_user, is_new=False, is_removal=False
):
    """
    Send notification when user employer assignments change.
    """
    user = organisation_employer_instance.epilepsy12_user

    if is_removal:
        action = "removed from"
        subject = f"Epilepsy12 User Removed from employer - {user.get_full_name()}"
    elif is_new:
        action = "assigned to"
        subject = f"Epilepsy12 User Assigned to employer - {user.get_full_name()}"
    else:
        action = "updated in"
        subject = (
            f"Epilepsy12 User employer Assignment Updated - {user.get_full_name()}"
        )

    # Get the display value for role
    role_display = user.get_role_display() if user.role else "Not specified"

    message = f"""
    A user's Organisation employer has been modified:

    User: {user.get_full_name()} ({user.email})
    Organisation: {organisation_employer_instance.employer_organisation.name} ({organisation_employer_instance.employer_organisation.trust})
    Action: User {action} Employer
    Modified by: {current_user.email if current_user else "System"}

    Role in Employer: {role_display}
    """
    # Send to audit team members
    try:
        if settings.CHANGE_NOTIFICATION_EMAILS:
            send_email_to_recipients(
                recipients=settings.CHANGE_NOTIFICATION_EMAILS, subject=subject, message=message
            )
            logger.info(f"Employer assignment notification sent for: {user.email}")
    except Exception as e:
        logger.error(
            f"Failed to send Employer assignment notification for user {user.email}: {e}"
        )
