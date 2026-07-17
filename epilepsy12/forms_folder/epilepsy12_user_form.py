from collections.abc import Iterator
from typing import Any
import logging

from django import forms
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    PasswordResetForm,
)
from django.utils.translation import gettext as _
from django.utils import timezone

from captcha.fields import CaptchaField

from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    TITLES,
)
from ..models import Epilepsy12User, Organisation, VisitActivity, OrganisationEmployer

# Logging setup
logger = logging.getLogger(__name__)


class Epilepsy12UserUpdatePasswordForm(SetPasswordForm):
    # form show when setting or resetting password
    # password validation occurs here and updates the password_last_set field
    is_admin = False

    def __init__(self, user, *args, **kwargs):
        self.user = user
        if (
            self.user.is_rcpch_audit_team_member
            or self.user.is_superuser
            or self.user.is_rcpch_staff
        ):
            self.is_admin = True
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        if self.is_admin and len(super().clean()["new_password1"]) < 16:
            raise forms.ValidationError(
                {
                    "new_password2": _(
                        "RCPCH audit team members must have passwords of 16 characters or more."
                    )
                }
            )
        return super().clean()

    def save(self, *args, commit=True, **kwargs):
        user = super().save(*args, commit=False, **kwargs)
        user.password_last_set = timezone.now()
        if commit:
            logger.debug(f"Updating password_last_set to {timezone.now()}")
            user.save()
            VisitActivity.objects.create(
                activity_datetime=timezone.now(),
                activity=5,
                ip_address=self.request.META.get("REMOTE_ADDR"),
                epilepsy12user=user,
            )
        return user


class Epilepsy12UserAdminCreationForm(forms.ModelForm):
    """
    This is a standard Django form to be used by admin to create a user without a password

    Just a word about readonly vs disabled fields. Standard django behaviour is to exclude
    disabled fields from the cleaned data. This means that if a field is disabled, it will not
    be included in the cleaned data and therefore not saved to the database. This is not
    desirable in this case, so we use readonly fields instead. Readonly fields are still included
    in the cleaned data, but they are not editable in the form. This means that the
    user cannot change the value of the field, but it will still be saved to the database
    when the form is submitted. However, because we are using semantic ui, readonly does not
    stop the field from being editable in the UI, so we also set the disabled attribute on the class
    to prevent the user from editing the field in the UI, but reenable it for RCPCH staff.

    This gives us the desired behaviour of allowing RCPCH staff to create users, edit their email addresses
    and change their organisation, but preventing other users from doing so.
    """

    rcpch_organisation = ""
    requesting_user = ""

    def __init__(self, rcpch_organisation, requesting_user, *args, **kwargs):
        super(Epilepsy12UserAdminCreationForm, self).__init__(*args, **kwargs)
        if rcpch_organisation == "organisation-staff":
            choices = AUDIT_CENTRE_ROLES
        elif rcpch_organisation == "rcpch-staff":
            choices = RCPCH_AUDIT_TEAM_ROLES
        else:
            raise ValueError(
                "No user-type supplied to create user form. Arguments are rcpch-staff or organisation-staff."
            )

        self.requesting_user = requesting_user
        self.rcpch_organisation = (
            rcpch_organisation  # this is used to determine the role choices
        )
        self.fields["role"].choices = choices

        if getattr(self, "initial", None):
            initial = getattr(self, "initial")
            if initial.get("email"):
                if (
                    requesting_user.is_superuser
                    or requesting_user.is_rcpch_staff
                    or requesting_user.is_rcpch_audit_team_member
                ):
                    self.fields["email"].widget.attrs["readonly"] = False
                    self.fields["email"].widget.attrs["disabled"] = False
                    self.fields["email"].widget.attrs.update(
                        {"class": "ui rcpch form input"}  # Editable styling
                    )
                else:
                    # if the user is not RCPCH staff, then the email field should be disabled
                    self.fields["email"].widget.attrs["readonly"] = True
                    self.fields["email"].widget.attrs.update(
                        {"class": "ui rcpch form disabled input"}  # Disabled styling
                    )
                user_to_edit = Epilepsy12User.objects.filter(
                    email=initial["email"].lower()
                )
                if user_to_edit.exists():
                    user_to_edit = user_to_edit.first()
                else:
                    # no user for this email address. should not really be possible
                    raise ValueError(
                        "No user found for the email address provided. Please check the email address."
                    )
            else:
                # unbound form. set the email field to enabled
                self.fields["email"].widget.attrs["readonly"] = False
                self.fields["email"].widget.attrs["disabled"] = False
                self.fields["email"].widget.attrs["placeholder"] = "Enter email address"
                self.fields["email"].widget.attrs.update(
                    {"class": "ui rcpch form input"}
                )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"class": "ui rcpch form input"},
        ),
        max_length=255,
        help_text="Required. Please enter a valid NHS email address.",
        required=True,
        validators=[validators.EmailValidator(message="Invalid Email")],
    )

    role = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "ui fluid rcpch dropdown"}),
        required=True,
    )

    title = forms.ChoiceField(
        choices=TITLES,
        widget=forms.Select(attrs={"class": "ui fluid rcpch dropdown"}),
        required=False,
    )

    first_name = forms.CharField(
        max_length=255, help_text="Please enter your first name", required=True
    )

    surname = forms.CharField(
        max_length=255, help_text="Please enter your surname", required=True
    )

    is_superuser = forms.BooleanField(initial=False, required=False)

    is_rcpch_audit_team_member = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "ui toggle checkbox"}),
        initial=False,
        required=False,
    )

    is_rcpch_staff = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "ui toggle checkbox"}),
        initial=False,
        required=False,
    )

    is_child_or_carer = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "ui toggle checkbox"}),
        initial=False,
        required=False,
    )

    email_confirmed = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "ui toggle checkbox"}),
        initial=False,
        required=False,
    )

    class Meta:
        model = Epilepsy12User
        fields = (
            "email",
            "role",
            "title",
            "first_name",
            "surname",
            "is_rcpch_staff",
            "is_rcpch_audit_team_member",
            "is_superuser",
            "email_confirmed",
        )

    def clean_email(self):
        cleaned_email = self.cleaned_data["email"].lower()

        if cleaned_email is not None:
            if Epilepsy12User.objects.filter(email=cleaned_email).exists():
                return cleaned_email
            # if editing email addresses is re-enabled in the UI then there needs to be
            # logic in here to prevent changing a user's email to an existing email address.

        else:
            # this is a new account - check email is unique
            if Epilepsy12User.objects.filter(email=cleaned_email).exists():
                raise forms.ValidationError(
                    "The email is already associated with an account."
                )

        return cleaned_email

    def clean_is_rcpch_audit_team_member(self):
        """
        if is_rcpch_audit_team_member is positive, set view_preference to organisation_view
        """
        data = self.cleaned_data["is_rcpch_audit_team_member"]
        if data:
            self.cleaned_data["view_preference"] = 0
        return data

    def clean_is_superuser(self):
        """
        if is_superuser is positive, set view_preference to organisation_view
        """
        data = self.cleaned_data["is_superuser"]
        if data:
            self.cleaned_data["view_preference"] = 0
        return data

    def clean_is_rcpch_staff(self):
        """
        if is_rcpch_staff is positive, set view_preference to organisation_view
        """
        data = self.cleaned_data["is_rcpch_staff"]
        if data:
            self.cleaned_data["view_preference"] = 0
        return data

    def clean(self):
        cleaned_data = super().clean()
        # new user being created is rcpch staff
        if self.rcpch_organisation == "rcpch-staff":
            # RCPCH staff are not affiliated with any organisation
            if (
                self.requesting_user.is_rcpch_audit_team_member
                or self.requesting_user.is_superuser
            ):
                cleaned_data["is_rcpch_staff"] = True
                cleaned_data["is_rcpch_audit_team_member"] = True
                cleaned_data["view_preference"] = 0
            else:
                # should not have managed to get here
                raise ValidationError(
                    "You do not have permission to create RCPCH staff."
                )
        else:
            # this new user being created  is not RCPCH staff
            if (
                self.requesting_user.is_rcpch_audit_team_member
                or self.requesting_user.is_superuser
            ):
                # anything goes
                return cleaned_data
            else:
                if cleaned_data["is_rcpch_audit_team_member"] == True:
                    self.add_error(
                        "is_rcpch_audit_team_member",
                        "You do not have permission to allocate RCPCH audit team member status.",
                    )
                if cleaned_data["is_rcpch_staff"] == True:
                    self.add_error(
                        "is_rcpch_staff",
                        "You do not have permission to allocate RCPCH staff member status.",
                    )
                if cleaned_data["is_superuser"] == True:
                    self.add_error(
                        "is_superuser",
                        "You do not have permission to allocate superuser status.",
                    )

        return cleaned_data


# IF IN DEBUG MODE, PRE-FILL CAPTCHA VALUE
class DebugCaptchaField(CaptchaField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.widgets[-1].attrs["value"] = "PASSED"


class CaptchaAuthenticationForm(AuthenticationForm):
    captcha = DebugCaptchaField() if settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA else CaptchaField()

    def __init__(self, request, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)

        # If bypassing 2FA/captcha for local dev -> don't require captcha, pre fill fields
        if settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA:
            logger.warning(
                f"IN LOCAL DEVELOPMENT, BYPASSING LOGIN BY PREFILLING FIELDS"
            )
            self.fields["username"].widget.attrs["value"] = (
                settings.LOCAL_DEV_ADMIN_EMAIL
                or "SET LOCAL_DEV_ADMIN_EMAIL IN ENVIRONMENT VARIABLES"
            )
            self.fields["password"].widget.attrs["value"] = (
                settings.LOCAL_DEV_ADMIN_PASSWORD
                or "SET LOCAL_DEV_ADMIN_PASSWORD IN ENVIRONMENT VARIABLES"
            )

    def clean_username(self) -> dict[str, Any]:
        email = super().clean()["username"]
        if email:
            try:
                user = Epilepsy12User.objects.get(email=email.lower()).DoesNotExist
            except Epilepsy12User.DoesNotExist:
                return super().clean()

            user = Epilepsy12User.objects.get(email=email.lower())

            visit_activities = VisitActivity.objects.filter(
                epilepsy12user=user
            ).order_by("-activity_datetime")[:5]

            failed_login_activities = [
                activity for activity in visit_activities if activity.activity == 2
            ]

            if failed_login_activities:
                first_activity = failed_login_activities[-1]

                if len(
                    failed_login_activities
                ) >= 5 and timezone.now() <= first_activity.activity_datetime + timezone.timedelta(
                    minutes=10
                ):
                    raise forms.ValidationError(
                        "You have failed to login 5 or more consecutive times. You have been locked out for 10 minutes"
                    )
            return email.lower()


class Epilepsy12PasswordResetForm(PasswordResetForm):
    """
    This is a standard Django form to be used by users to reset their password
    It is not possible in standard Django for users to reset their passwords if their account is inactive or they have an unusable password.
    Since new accounts are created with unusable passwords, if a user fails to confirm their email address they will be unable to reset their password.
    This form is overridden to allow users to reset their password if their account has an unusable password. This still have to be active users
    """

    def get_users(self, email: str):
        return Epilepsy12User.objects.filter(
            email__iexact=email, is_active=True
        )  # only return active users including those with unusable passwords
