
from django import forms
from django.core import validators
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm, AuthenticationForm
from epilepsy12.constants.user_types import ROLES, TITLES
from ..models import Epilepsy12User, Organisation


class Epilepsy12LoginForm(AuthenticationForm):

    class Meta:
        model = Epilepsy12User
        fields = ("username", "password")

    def clean_username(self):
        data = self.cleaned_data['username']
        return data.lower()


class Epilepsy12UserCreationForm(UserCreationForm):

    title = forms.CharField(
        required=False
    )

    email = forms.EmailField(
        max_length=255,
        help_text="Required. Please enter a valid NHS email address.",
        required=True
    )

    role = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={'class': 'ui fluid rcpch dropdown'}),
        required=True
    )

    organisation_employer = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.Select(
            attrs={'class': 'ui fluid search rcpch dropdown', 'readonly': True}),
        required=False
    )

    first_name = forms.CharField(
        max_length=255,
        help_text='Please enter your first name',
        required=True
    )

    surname = forms.CharField(
        max_length=255,
        help_text='Please enter your surname',
        required=True
    )

    is_rcpch_audit_team_member = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'}),
        required=True
    )

    is_staff = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'}),
        required=True
    )

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "organisation_employer", 'first_name', 'surname',
                  "is_rcpch_audit_team_member", 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs) -> None:
        super(Epilepsy12UserCreationForm, self).__init__(*args, **kwargs)


class Epilepsy12UserChangeForm(UserChangeForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "organisation_employer", 'first_name', 'surname',
                  "is_rcpch_audit_team_member", 'is_staff', 'is_active')


class Epilepsy12UserAdminCreationForm(UserCreationForm):
    """
    This is a standard Django form to be used by admin to create a user without a password
    """
    admin_title = forms.CharField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(Epilepsy12UserAdminCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.user_existing_email = self.instance.email

    email = forms.EmailField(
        max_length=255,
        help_text="Required. Please enter a valid NHS email address.",
        required=True, validators=[validators.EmailValidator(message="Invalid Email")]
    )

    role = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={'class': 'ui fluid rcpch dropdown'}),
        required=True
    )

    organisation_employer = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.Select(
            attrs={'class': 'ui fluid search rcpch disabled dropdown'})
    )

    title = forms.ChoiceField(
        choices=TITLES,
        widget=forms.Select(attrs={'class': 'ui fluid rcpch dropdown'}),
        required=False
    )

    first_name = forms.CharField(
        max_length=255,
        help_text='Please enter your first name',
        required=True
    )

    surname = forms.CharField(
        max_length=255,
        help_text='Please enter your surname',
        required=True
    )

    is_superuser = forms.BooleanField(
        initial=False,
        required=False
    )

    is_rcpch_audit_team_member = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'}),
        initial=False,
        required=False
    )

    is_staff = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'}),
        initial=False,
        required=False
    )

    email_confirmed = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'}),
        initial=False,
        required=False
    )

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "organisation_employer", 'title', 'first_name', 'surname', "is_staff",
                  "is_rcpch_audit_team_member", "is_superuser", "email_confirmed")

    def clean_email(self):
        data = self.cleaned_data['email']
        if self.user_existing_email is not None:
            # this user is being updated
            if self.user_existing_email != data.lower():
                # test to check this email does not exist
                if Epilepsy12User.objects.filter(email=data.lower()).exists():
                    raise forms.ValidationError(
                        f"{data.lower()} is already associated with an account.")
        else:
            # this is a new account - check email is unique
            if Epilepsy12User.objects.filter(email=data.lower()).exists():
                raise forms.ValidationError(
                    "The email is already associated with an account.")

        return data.lower()


class Epilepsy12UserPasswordResetForm(SetPasswordForm):
    """Change password form."""
    new_password1 = forms.CharField(label='Password',
                                    help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(
                                        attrs={
                                            'class': 'form-control',
                                            'placeholder': 'password',
                                            'type': 'password',
                                            'id': 'user_password',
                                        }))

    new_password2 = forms.CharField(label='Confirm password',
                                    help_text=False,
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(
                                        attrs={
                                            'class': 'form-control',
                                            'placeholder': 'confirm password',
                                            'type': 'password',
                                            'id': 'user_password',
                                        }))

    def clean(self):
        cleaned_data = super(Epilepsy12UserPasswordResetForm, self).clean()
        print("cleaning reset password form")
        return cleaned_data


class UserForgotPasswordForm(PasswordResetForm):
    """User forgot password, check via email form."""
    email = forms.EmailField(label='Email address',
                             max_length=254,
                             required=True,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': 'email address',
                                        'type': 'text',
                                        'id': 'email_address'
                                        }
                             ))

    def clean(self):
        print("cleaning passwordresetform")
        cleaned_data = super(UserForgotPasswordForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        print("saving passwordresetform")
        # Save the provided password in hashed format
        user = super(UserForgotPasswordForm, self).save(commit=False)

        if commit:
            user.save()
        return user
