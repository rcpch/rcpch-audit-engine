from django.core.exceptions import PermissionDenied
from django.apps import apps


def return_selected_organisation(user):
    """
    Function called from organisation views
    Returns the selected hospital based on user affiliation. If an RCPCH member and no hospital affilation
    the first in the list is returned. Otherwise, an error is raised
    Accepts a user object.
    """

    Organisation = apps.get_model("epilepsy12", "Organisation")

    if user.organisation_employer is not None:
        # current user is affiliated with an existing organisation - set viewable trust to this
        return Organisation.objects.get(name=user.organisation_employer)
    else:
        # current user is NOT affiliated with an existing organisation
        if user.is_rcpch_staff or user.is_superuser or user.is_superuser:
            # current user is a member of the RCPCH audit team and also not affiliated with a organisation
            # therefore set selected organisation to first of organisation on the list
            return Organisation.objects.order_by("name").first()
        else:
            # Imposter! You shall not pass!
            raise PermissionDenied()


def sanction_user(user):
    if user.organisation_employer is not None:
        # current user is affiliated with an existing organisation - set viewable trust to this
        return True
    else:
        # current user is NOT affiliated with an existing organisation
        if user.is_rcpch_staff or user.is_superuser or user.is_superuser:
            # current user is a member of the RCPCH audit team and also not affiliated with a organisation
            # therefore set selected organisation to first of organisation on the list
            return True
        else:
            # Imposter! You shall not pass!
            raise PermissionDenied()
