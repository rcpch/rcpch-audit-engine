import string

from django_unicorn.components import UnicornView
from django.contrib.auth.decorators import login_required
from ..models import DESSCRIBE
from ..models import Keyword


# @login_required
class DesscribeView(UnicornView):
    description: str = ""
    collected_keywords = []
    choices: list = Keyword.objects.all()
    desscribe = DESSCRIBE.objects.none()
    case_id = ""

    # def __init__(self, *args, **kwargs):
    #     super().__init__(**kwargs)  # calling super is required
    #     case_id = kwargs.get("case_id")
    #     print(case_id)

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
                self.collected_keywords.append(word)
        # secondary sort by category
        self.collected_keywords.sort(key=lambda tup: tup[1])

    # def delete_desscribe(self, id):
    #     # try:
    #     #     # desscribe = DESSCRIBE.objects.get(id=id)
    #     #     # desscribe.delete()
    #     # except:
    #     #     pass
    #     print("delete")
