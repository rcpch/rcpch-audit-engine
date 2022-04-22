from ..models import Epilepsy12User

from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class Epilepsy12UserCreationForm(UserCreationForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_trust")


class Epilepsy12UserChangeForm(UserChangeForm):

    class Meta:
        model = Epilepsy12User
        fields = ("email", "role", "hospital_trust")
