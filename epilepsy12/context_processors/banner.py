import re

from django.core.cache import cache

from ..models import Banner

def banner(request):
    banners = cache.get("banner")

    if not banners:
        banners = Banner.objects.all()
        cache.set("banner", banners, timeout=10)

    for banner in banners:
        url_matcher = re.compile(banner.url_matcher)

        if url_matcher.match(request.path) and not banner.disabled:
            if banner.user_role_to_target and request.user:
                if request.user.role == banner.user_role_to_target or request.user.is_rcpch_audit_team_member:
                    return { "banner": banner }
            elif not banner.user_role_to_target:
                return { "banner": banner }

    return {}