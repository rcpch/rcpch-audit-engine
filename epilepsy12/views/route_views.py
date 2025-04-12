from django.shortcuts import render

from epilepsy12.models import Organisation
from epilepsy12.constants import INDIVIDUAL_KPI_MEASURES


def index(request):
    """
    This is the landing page for all site visitors. Any navigation on from here requires the user to login,
    except the children and families page which requires an organisation id to filter against. An organisation is chosen
    here at random, but in future might be chosen based on the location of the visitor's ISP.
    """
    # if getattr(request.user, "organisation_employer", None) is not None:
    organisation = Organisation.objects.get(name=request.user.organisation_employer)
    # else:
    #     organisation = Organisation.objects.order_by("?").first()
    template_name = "epilepsy12/epilepsy12index.html"
    context = {"organisation": organisation}
    return render(request=request, template_name=template_name, context=context)


# def open_access(request, organisation_id):
#     """
#     Landing page for children and families - takes an organisation_id to present
#     the KPI table for that organisation, as well as load the dropdown with all organisations.
#     """
#     template_name = "epilepsy12/open_access.html"
#     organisation = Organisation.objects.get(pk=organisation_id)
#     context = {
#         "organisation": organisation,
#         "organisation_list": Organisation.objects.filter(active=True).order_by("name"),
#         "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
#     }
#     return render(request, template_name, context=context)


def documentation(request):
    """
    Deprecated - docs are now hosted elsewhere
    """
    template_name = "epilepsy12/docs.html"
    return render(request, template_name, {})
