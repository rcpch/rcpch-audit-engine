from dal import autocomplete
from ..models import HospitalTrust


class HospitalAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HospitalTrust.objects.none()

        qs = HospitalTrust.objects.filter(
            Sector__iexact="NHS Sector").order_by('OrganisationName')
        if self.q:
            qs = qs.filter(OrganisationName__istartswith=self.q)
        return qs
