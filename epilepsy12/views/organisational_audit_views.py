from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def _organisational_audit(request, group_name, submission_period, submission):
    context = {
        "group_name": group_name,
        "submission_period": submission_period,
        "form": OrganisationalAuditSubmissionForm(submission)
    }
    
    if request.method == "POST":
        context["form"] = OrganisationalAuditSubmissionForm(request.POST)
        context["form"].save()

        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()

    trust = Trust.objects.get(id=id)

    submission = None
    if submission_period.submissions:
        submission = submission_period.submissions.filter(trust=trust).first()

    return _organisational_audit(request, trust.name, submission_period, submission)

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()
    
    local_health_board = LocalHealthBoard.objects.get(id=id)

    submission = None
    if submission_period.submissions:
        submission = submission_period.submissions.filter(local_health_board=local_health_board).first()

    return _organisational_audit(request, local_health_board.name, submission_period, submission)