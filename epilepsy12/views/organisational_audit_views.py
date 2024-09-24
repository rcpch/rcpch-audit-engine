from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def _organisational_audit(request, group_name):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()

    context = {
        "group_name": group_name,
        "submission_period": submission_period,
        "form": OrganisationalAuditSubmissionForm()
    }
    
    if request.method == "POST":
        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    trust = Trust.objects.get(id=id)

    return _organisational_audit(request, trust.name)

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    local_health_board = LocalHealthBoard.objects.get(id=id)

    return _organisational_audit(request, local_health_board.name)