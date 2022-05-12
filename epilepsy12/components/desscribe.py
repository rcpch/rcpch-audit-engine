import string

from django_unicorn.components import UnicornView
from django.contrib.auth.decorators import login_required
from ..models import DESSCRIBE
from ..models import Case
from ..models import Keyword


# @login_required
class DesscribeView(UnicornView):
    description: str = ""
    collected_keywords = []
    choices: list = Keyword.objects.all()
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
                print("last value typed is a space")
            desscribe = DESSCRIBE(description=self.description)
            desscribe.save()
            print(self.description)
        self.description = ""

    def textUpdated(self):
        # split string into array of words without punctuation
        all_words = self.description.lower().strip(string.punctuation)

        keywords = Keyword.objects.values_list('keyword', 'category')
        # identify where keywords match
        for index, word in enumerate(keywords):
            if word[0] in all_words:
                self.collected_keywords.append(
                    {'index': index, 'word': word[0], 'category': word[1]})
        # secondary sort by category
        self.collected_keywords.sort(key=lambda tup: tup['category'])

    def remove(self, index):
        item = next(
            keyword for keyword in self.collected_keywords if keyword['index'] == index)
        self.collected_keywords.remove(item)
