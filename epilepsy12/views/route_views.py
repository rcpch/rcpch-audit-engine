from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from epilepsy12.models import Organisation


@login_required
def index(request):
    """
    This is the landing page for all site visitors. Any navigation on from here requires the user to login,
    except the children and families page which requires an organisation id to filter against. An organisation is chosen
    here at random, but in future might be chosen based on the location of the visitor's ISP.
    """
    organisation = Organisation.objects.get(name=request.user.organisation_employer)
    template_name = "epilepsy12/epilepsy12index.html"
    context = {"organisation": organisation}
    return render(request=request, template_name=template_name, context=context)
