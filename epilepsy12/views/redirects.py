from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.http import FileResponse, HttpRequest, HttpResponse
from django.urls import reverse_lazy

# 3rd party
from django_htmx.http import HttpResponseClientRedirect


# @require_GET
# @cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
# def favicon(request: HttpRequest) -> HttpResponse:
#     file = (settings.BASE_DIR / "static" / "images/favicon-16x16.png").open("rb")
#     return FileResponse(file)


def rcpch_403(request, exception):
    # this view is necessary to trigger a page refresh
    # it is called on raise PermissionDenied()
    # If a 403 template were to be returned at this point as in standard django,
    # the 403 template would be inserted into the target. This way the HttpReponseClientRedirect
    # from django-htmx middleware forces a redirect to the two-factor sign-in page
    if request.htmx:
        return HttpResponseClientRedirect('two_factor:login', status=403)
    else:
        return redirect('two_factor:login')


def redirect_403(request):
    # return the custom 403 template. There is no context to add.
    return render(
        request,
        template_name="epilepsy12/error_pages/rcpch_403.html",
        context={},
        status=403,
    )


def rcpch_404(request, exception):
    # return the custom 404 template. There is no context to add.
    return render(
        request, template_name="epilepsy12/error_pages/rcpch_404.html", context={}
    )


def rcpch_500(request):
    # return the custom 500 template. There is no context to add.
    return render(
        request, template_name="epilepsy12/error_pages/rcpch_500.html", status=500
    )
