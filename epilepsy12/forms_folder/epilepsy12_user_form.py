
from django import forms
from django.core import validators
from epilepsy12.constants.user_types import ROLES, TITLES
from ..models import Epilepsy12User, HospitalTrust

from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class Epilepsy12UserCreationForm(UserCreationForm):

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

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = Epilepsy12User.objects.get(email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"{email} already in use!")

    def clean_password2(self) -> str:
        password2 = super().clean_password2()
        print("I get called")
        return "Epilepsy12User"

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)

        if commit:
            user.save()
        return user


class Epilepsy12UserChangeForm(UserChangeForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer",
                  "is_rcpch_audit_team_member")


class Epilepsy12UserAdminCreationForm(UserCreationForm):
    """
    This is a standard Django form to be used by admin to create a user without a password
    """
    title = forms.CharField()

    def __init__(self, *args, **kwargs) -> None:
        super(Epilepsy12UserAdminCreationForm, self).__init__(*args, **kwargs)
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
        required=False
    )

    is_rcpch_audit_team_member = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'})
    )

    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'ui toggle checkbox'})
    )

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer", 'title', 'first_name', 'surname', "is_staff",
                  "is_rcpch_audit_team_member")

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = Epilepsy12User.objects.get(email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"{email} already in use!")

    def clean_password1(self) -> str:
        return "Epilepsy12User"

    def clean_password2(self) -> str:
        return "Epilepsy12User"

    def clean(self):
        print("cleaning...")
        cleaned_data = super(Epilepsy12UserAdminCreationForm, self).clean()
        # Get the field values from cleaned_data dict
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        print("save called")
        user = super(Epilepsy12UserAdminCreationForm, self)
        self.clean()
        user.save(commit=False)

        if commit:
            user.save()
        return user
