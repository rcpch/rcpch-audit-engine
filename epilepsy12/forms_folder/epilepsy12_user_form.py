from django import forms
from django.core import validators
from django.contrib.auth.forms import (
    PasswordResetForm,
    SetPasswordForm,
    AuthenticationForm,
)
from epilepsy12.constants.user_types import (
    ROLES,
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    TITLES,
)
from ..models import Epilepsy12User, Organisation
from ..general_functions import match_in_choice_key


class Epilepsy12LoginForm(AuthenticationForm):
    class Meta:
        model = Epilepsy12User
        fields = ("username", "password")

    def clean_username(self):
        data = self.cleaned_data["username"]
        return data.lower()


class Epilepsy12UserAdminCreationForm(forms.ModelForm):  # UserCreationForm
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

    email = forms.EmailField(
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


class Epilepsy12UserPasswordResetForm(SetPasswordForm):
    """Change password form."""

    new_password1 = forms.CharField(
        label="Password",
        help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "password",
                "type": "password",
                "id": "user_password",
            }
        ),
    )

    new_password2 = forms.CharField(
        label="Confirm password",
        help_text=False,
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "confirm password",
                "type": "password",
                "id": "user_password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super(Epilepsy12UserPasswordResetForm, self).clean()
        return cleaned_data


class UserForgotPasswordForm(PasswordResetForm):
    """User forgot password, check via email form."""

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "email address",
                "type": "text",
                "id": "email_address",
            }
        ),
    )

    def clean(self):
        cleaned_data = super(UserForgotPasswordForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserForgotPasswordForm, self).save(commit=False)

        if commit:
            user.save()
        return user
