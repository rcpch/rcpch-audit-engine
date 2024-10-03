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
from ..models import Epilepsy12User, Organisation, VisitActivity

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
        self.rcpch_organisation = rcpch_organisation
        self.fields["role"].choices = choices

        if getattr(self, "initial", None):
            initial = getattr(self, "initial")
            if initial.get("email"):
                self.fields["email"].widget.attrs["disabled"] = True

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

    organisation_employer = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.Select(attrs={"class": "ui fluid search rcpch disabled dropdown"}),
        required=False,
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

    is_staff = forms.BooleanField(
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
            "organisation_employer",
            "title",
            "first_name",
            "surname",
            "is_staff",
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

    # def clean_organisation_employer(self):
    #     data = self.cleaned_data["organisation_employer"]
    #     return data

    def clean(self):
        cleaned_data = super().clean()
        if self.rcpch_organisation == "rcpch-staff":
            # RCPCH staff are not affiliated with any organisation
            if (
                self.requesting_user.is_rcpch_audit_team_member
                or self.requesting_user.is_superuser
            ):
                cleaned_data["is_staff"] = False
                cleaned_data["is_rcpch_staff"] = True
                cleaned_data["organisation_employer"] = None
                cleaned_data["is_rcpch_audit_team_member"] = True
                cleaned_data["view_preference"] = 0
            else:
                # should not have managed to get here
                raise ValidationError(
                    "You do not have permission to create RCPCH staff."
                )
        else:
            # this new user is not RCPCH staff
            if (
                self.requesting_user.is_rcpch_audit_team_member
                or self.requesting_user.is_superuser
            ):
                # anything goes
                return cleaned_data
            else:
                if (
                    self.requesting_user.organisation_employer
                    != cleaned_data["organisation_employer"]
                ):
                    # nonmatching organisations might still be in the same health board or trust
                    requested_organisation = Organisation.objects.get(
                        name=cleaned_data["organisation_employer"]
                    )
                    if (
                        requested_organisation.country.boundary_identifier
                        == "W92000004"
                    ):
                        requested_parent = requested_organisation.local_health_board
                        requesting_parent = (
                            self.requesting_user.organisation_employer.local_health_board
                        )
                    else:
                        requested_parent = requested_organisation.trust
                        requesting_parent = (
                            self.requesting_user.organisation_employer.trust
                        )

                    if requested_parent == requesting_parent:
                        # members of the same trust
                        # your papers are in order...
                        pass
                    else:
                        self.add_error(
                            "organisation_employer",
                            "You do not have permission to create users in different trusts or local health boards.",
                        )
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
    captcha = DebugCaptchaField() if settings.DEBUG else CaptchaField()

    def __init__(self, request, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)

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
