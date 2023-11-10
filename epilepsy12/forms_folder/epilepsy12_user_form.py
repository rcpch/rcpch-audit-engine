from typing import Any
from django import forms
from django.conf import settings
from django.core import validators
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext as _
from django.utils import timezone

from captcha.fields import CaptchaField

from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    TITLES,
)
from ..models import Epilepsy12User, Organisation, VisitActivity


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
            print(f"Updating password_last_set to {timezone.now()}")
            user.save()
        return user


class Epilepsy12UserAdminCreationForm(forms.ModelForm):
    """
    This is a standard Django form to be used by admin to create a user without a password
    """

    rcpch_organisation = ""

    def __init__(self, rcpch_organisation, *args, **kwargs):
        super(Epilepsy12UserAdminCreationForm, self).__init__(*args, **kwargs)
        if rcpch_organisation == "organisation-staff":
            choices = AUDIT_CENTRE_ROLES
        elif rcpch_organisation == "rcpch-staff":
            choices = RCPCH_AUDIT_TEAM_ROLES
        else:
            raise ValueError(
                "No user-type supplied to create user form. Arguments are rcpch-staff or organisation-staff."
            )

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
        data = self.cleaned_data["email"]

        if data is not None:
            if Epilepsy12User.objects.filter(email=data.lower()).exists():
                return data.lower()

            # this user is being updated
            if data != data.lower():
                # test to check this email does not exist
                if Epilepsy12User.objects.filter(email=data.lower()).exists():
                    raise forms.ValidationError(
                        f"{data.lower()} is already associated with an account."
                    )
        else:
            # this is a new account - check email is unique
            if Epilepsy12User.objects.filter(email=data.lower()).exists():
                raise forms.ValidationError(
                    "The email is already associated with an account."
                )

        return data.lower()

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

    def clean_organisation_employer(self):
        data = self.cleaned_data["organisation_employer"]
        return data

    def clean(self):
        cleaned_data = super().clean()

        if self.rcpch_organisation == "rcpch-staff":
            # RCPCH staff are not affiliated with any organisation
            cleaned_data["is_staff"] = False
            cleaned_data["is_rcpch_staff"] = True
            cleaned_data["organisation_employer"] = None
            cleaned_data["is_rcpch_audit_team_member"] = True
            cleaned_data["view_preference"] = 0

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
        email = self.cleaned_data["username"]
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

        return super().clean()
