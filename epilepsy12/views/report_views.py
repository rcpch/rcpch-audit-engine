from django.shortcuts import render

from ..decorator import login_and_otp_required, rcpch_full_access_only

@login_and_otp_required()
@rcpch_full_access_only()
def submission_dashboard(request):
    context = {}
    return render(request, "epilepsy12/submission_dashboard.html", context)