
from epilepsy12.constants.user_types import ROLES
from ..models import Epilepsy12User, HospitalTrust
from django import forms

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
        widget=forms.Select(attrs={'class': 'ui fluid search rcpch dropdown'}),
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

    class Meta:
        model = Epilepsy12User
        fields = ("username", "email", "role", "hospital_employer", 'first_name', 'surname',
                  "is_rcpch_audit_team_member", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = Epilepsy12User.objects.get(email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"{email} already in use!")

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        try:
            user = Epilepsy12User.objects.get(username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"{username} already in use!")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class Epilepsy12UserChangeForm(UserChangeForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_employer",
                  "is_rcpch_audit_team_member")
