"""
Custom permissions for API - these permissions are not applied to the views
"""

# Python imports

# Django imports
from rest_framework import permissions

# 3rd party imports

# E12 imports


class CanAccessOrganisation(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # superusers and RCPCH audit team members can acccess all organisations
        if request.user.is_superuser or request.user.is_rcpch_audit_team_member:
            return True

        return False
