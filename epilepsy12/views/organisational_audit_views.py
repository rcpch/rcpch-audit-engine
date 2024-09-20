from django.shortcuts import render

from ..decorator import (
    login_and_otp_required,
)

@login_and_otp_required()
def organisational_audit(request, id):
    context = {}
    template_name = "epilepsy12/organisational_audit.html"
    return render(request, template_name, context)