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
        try:
            self.desscribe = DESSCRIBE.objects.get(
                registration=self.registration)
            self.collected_keywords = self.desscribe.description_keywords
        except:
            self.desscribe = None

    def add(self):
        if self.description != "":
            if self.description.endswith(' '):
                desscribe = DESSCRIBE.objects.update_or_create(
                    description=self.description, defaults={'registration': self.registration})

        self.description = ""

    def textUpdated(self):
        """
        on input change the user input is scanned for near match keywords
        and stored in the self.description model
        """
        self.collected_keywords = fuzzy_scan_for_keywords(
            self.description, self.choices)
        print(self.collected_keywords)
        # desscribe = DESSCRIBE.objects.update_or_create(
        #     description=self.description, description_keywords=self.collected_keywords, defaults={'registration': self.registration})

    def remove_keyword(self, index):
        item = next(
            keyword for keyword in self.collected_keywords if keyword['pk'] == index)
        self.collected_keywords.remove(item)

    """
    DUMMY TEXT
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed egestas congue vulputate. Pellentesque scelerisque, ex sit amet hendrerit malesuada, felis augue rhoncus neque, et dapibus diam magna ac elit. Etiam dapibus porta incoordination massa, ultricies pharetra neque fringilla non. Nunc ornare in ante vel viverra. Donec sit amet eleifend sem. Cras gravida suscipit risus eget blandit. Nulla vitae molestie elit. Sed nisl dolor, iaculis eget ornare elementum, tristique ornare urna. Proin velit felis, venenatis at ipsum sed, fermentum viverra sapien. Curabitur leo felis, tempor ac urna eget, ultrices ultrices ipsum. Morbi scelerisque mi sapien, at maximus nulla finibus et. Nullam sollicitudin aliquet felis. Proin id mauris dui. Donec dignissim odio in tellus dictum, nec scelerisque leo elementum.
    Curabitur rutrum vestibulum placerat. Aenean varius, erat ut ornare tristique, leo lacus jacksonian hendrerit orci, pharetra maximus metus ante id velit. Proin rutrum urna in sem tempor ullamcorper. Integer malesuada tellus quis velit cursus, sit amet gravida urna commodo. Donec pretium lorem ut leo pellentesque elementum. Cras sit amet lorem venenatis, fringilla elit sit amet, volutpat diam. Ut ullamcorper gravida tristique. Integer pretium sagittis nulla posuere pretium. Aliquam erat volutpat. Sed quam nulla, tincidunt a pharetra vestibulum, iaculis blandit augue. Aliquam erat volutpat. Etiam orci mi, scelerisque vel ligula ut, semper dictum tortor. Fusce vitae efficitur purus, vel varius eros. Suspendisse dapibus finibus mauris vel sollicitudin. Curabitur rhoncus, lorem quis mattis porta, nibh libero hendrerit massa, eget vulputate erat velit ac nisi. Pellentesque ac eleifend orci, nec tristique dolor.
    Integer tempor efficitur velit ac interdum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean tincidunt, lacus sit amet molestie efficitur, sem dui fermentum purus, quis venenatis diam neque sit amet dui. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse aliquet a diam ut ornare. In eleifend, risus sed iaculis auctor, nisi tortor porttitor odio, et dictum tortor tortor vel lectus. Integer non nulla imperdiet, maximus turpis ac, scelerisque risus. Phasellus tempor dolor vel enim convallis, a congue ligula fringilla. Etiam sollicitudin velit eget ultrices interdum. Aliquam pretium vehicula pretium. Nulla facilisi.
    Curabitur consequat, felis eu iaculis facilisis, lorem massa pretium ante, vitae lacinia tortor erat non tortor. Maecenas scelerisque ultricies finibus. Aenean eros lectus, elementum ac tellus elementum, congue blandit elit. Quisque olfactory et sem a metus malesuada ultrices in sed eros. Etiam ac risus vel ligula euismod pellentesque. Etiam eget ullamcorper nisl. Cras dictum est massa, quis malesuada augue pellentesque at. Sed semper enim a nibh convallis fringilla. Phasellus lacinia feugiat magna accumsan finibus.Quisque sed dui neque. Pellentesque hendrerit, elit et mollis dignissim, lorem neque facilisis dui, eget sagittis arcu metus lobortis mauris. Nunc et nulla ullamcorper, suscipit lacus at, tempus orci. Duis fermentum quam sapien, at efficitur visual est vestibulum at. Ut eget left pretium diam, eget lacinia libero. Donec vel imperdiet orci. Duis vestibulum vestibulum mattis. Curabitur right neque mauris, viverra eget est quis, tristique mollis arcu.
    """
