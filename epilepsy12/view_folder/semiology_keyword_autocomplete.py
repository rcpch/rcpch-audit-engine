from ast import keyword
from dal import autocomplete
from ..models import Keyword


class SemiologyKeywordAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        print(self)
        if not self.request.user.is_authenticated:
            return Keyword.objects.none()
        qs = Keyword.objects.all().order_by('keyword')
        if self.q:
            qs.filter(keyword__iexact=self.q)
        return qs
