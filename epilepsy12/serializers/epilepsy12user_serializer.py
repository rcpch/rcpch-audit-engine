# Python imports
from datetime import datetime

# Django imports
from django.contrib.auth.models import Group

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import *


class Epilepsy12UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Epilepsy12User
        fields = [
            "first_name",
            "surname",
            "title",
            "email",
            "username",
            "is_active",
            "is_staff",
            "is_rcpch_staff",
            "is_superuser",
            "is_rcpch_audit_team_member",
            "view_preference",
            "date_joined",
            "role",
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]
