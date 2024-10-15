import re
from ..models import Banner

def banner(request):
    banners = Banner.objects.all()

    for banner in banners:
        url_matcher = re.compile(banner.url_matcher)

        if url_matcher.match(request.path):
            return { "banner": banner }

    return {}