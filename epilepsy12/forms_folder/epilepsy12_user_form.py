
from django import forms
from django.core import validators
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm, AuthenticationForm
from epilepsy12.constants.user_types import ROLES, TITLES
from ..models import Epilepsy12User, HospitalTrust


class Epilepsy12LoginForm(AuthenticationForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "password")


class Epilepsy12UserCreationForm(UserCreationForm):

    title = forms.CharField()

    email = forms.EmailField(
        max_length=255,
        help_text="Required. Please enter a valid NHS email address."
    )

    role = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={'class': 'ui fluid rcpch dropdown'})
    )

    hospital_employer = forms.ModelChoiceField(
        queryset=HospitalTrust.objects.all(),
        widget=forms.Select(
            attrs={'class': 'ui fluid search rcpch dropdown', 'readonly': True}),
        required=False
    )

    first_name = forms.CharField(
        max_length=255,
        help_text='Please enter your first name',
    )

    surname = forms.CharField(
        max_length=255,
        help_text='Please enter your surname'
    )

    is_rcpch_audit_team_member = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'})
    )

    is_staff = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'})
    )

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer", 'first_name', 'surname',
                  "is_rcpch_audit_team_member", 'is_staff', 'is_active')


class Epilepsy12UserChangeForm(UserChangeForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer", 'first_name', 'surname',
                  "is_rcpch_audit_team_member", 'is_staff', 'is_active')


class Epilepsy12UserAdminCreationForm(UserCreationForm):
    """
    This is a standard Django form to be used by admin to create a user without a password
    """
    admin_title = forms.CharField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    email = forms.EmailField(
        max_length=255,
        help_text="Required. Please enter a valid NHS email address.",
        initial='Enter your email', required=True, validators=[validators.EmailValidator(message="Invalid Email")]
    )

    role = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={'class': 'ui fluid rcpch dropdown'}),
        required=True
    )

    hospital_employer = forms.ModelChoiceField(
        queryset=HospitalTrust.objects.all(),
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
        help_text='Please enter your first name'
    )

    surname = forms.CharField(
        max_length=255,
        help_text='Please enter your surname'
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

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer", 'title', 'first_name', 'surname', "is_staff",
                  "is_rcpch_audit_team_member", "is_superuser", "email_confirmed")

    def clean(self):
        cleaned_data = super(Epilepsy12UserAdminCreationForm, self).clean()
        return cleaned_data


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
