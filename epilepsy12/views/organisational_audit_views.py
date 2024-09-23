from django.shortcuts import render

from ..models import Trust, LocalHealthBoard

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    context = {}
    template_name = "epilepsy12/organisational_audit.html"
    return render(request, template_name, context)

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    context = {}
    template_name = "epilepsy12/organisational_audit.html"
    return render(request, template_name, context)