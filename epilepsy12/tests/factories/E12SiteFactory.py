"""Factory fn to create new E12 Sites

A new site is create automatically once `E12CaseFactory.create()` is called.
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Organisation,
    Site,
)


class E12SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site

    # define many to many relationship
    case = None

    # define many to many relationship
    organisation = factory.Iterator(Organisation.objects.all())

    site_is_actively_involved_in_epilepsy_care = True
    site_is_primary_centre_of_epilepsy_care = True
