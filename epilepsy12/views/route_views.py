from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    template_name = "epilepsy12/epilepsy12index.html"
    context = {"organisation": request.user.organisation_employer}
    return render(request=request, template_name=template_name, context=context)
