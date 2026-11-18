"""
Custom permissions for API - these permissions are not applied to the views
"""

# Python imports

# Django imports
from rest_framework import permissions

from epilepsy12.constants.user_types import PERM_ACCESS_ALL_ORGANISATIONS

# 3rd party imports

# E12 imports


class CanAccessOrganisation(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # superusers and RCPCH audit team members can access all organisations
        if request.user.has_perm(PERM_ACCESS_ALL_ORGANISATIONS):
            return True

        return False
