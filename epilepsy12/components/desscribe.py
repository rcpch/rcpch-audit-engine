from random import choices
from django_unicorn.components import UnicornView

from epilepsy12.general_functions import desscribe
from ..models import DESSCRIBE
from ..models import Case
from ..models import Keyword

from ..general_functions.fuzzy_matching import scan_for_keywords, fuzzy_scan_for_keywords


class DesscribeView(UnicornView):
    description: str = ""
    collected_keywords = []
    choices = Keyword.objects.all()
    desscribe = DESSCRIBE.objects.none()
    case_id = ""
    registration = ""
    name = ""

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.case_id = kwargs.get("case_id")
        self.registration = kwargs.get("registration")
        self.name = Case.objects.get(pk=self.case_id)

    def add(self):
        if self.description != "":
            if self.description.endswith(' '):
                desscribe = DESSCRIBE(description=self.description)
                # desscribe.save()
                print(self.description)
        self.description = ""

    def textUpdated(self):
        """
        on input change the user input is scanned for near match keywords
        and stored in the self.description model
        """
        self.collected_keywords = fuzzy_scan_for_keywords(
            self.description, self.choices)
        desscribe = DESSCRIBE(description=self.description,
                              description_keywords=self.collected_keywords, registration=self.registration)
        # desscribe.save()

    def remove_keyword(self, index):
        item = next(
            keyword for keyword in self.collected_keywords if keyword['index'] == index)
        self.collected_keywords.remove(item)
