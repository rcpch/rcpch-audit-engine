"""
Django Rest Framework Registration Viewset
"""

# python
from datetime import datetime

# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers

# third party
from epilepsy12.serializers.registration_serializer import RegistrationSerializer

from epilepsy12.models import (
    Case,
    Organisation,
    Site,
    Registration,
    FirstPaediatricAssessment,
    EpilepsyContext,
    MultiaxialDiagnosis,
    Assessment,
    Management,
    Investigations,
    KPI,
    AuditProgress,
)
from epilepsy12.permissions import CanAccessOrganisation


class RegistrationViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows registrations in Epilepsy12 to be viewed.
    """

    queryset = Registration.objects.all().order_by("-first_paediatric_assessment_date")
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def register_case_in_E12(self, request):
        """
        Create an active registration in the audit.
        Essential parameters:
        nhs_number: 10 digit number
        lead_centre: OrganisationID
        first_paediatric_assessment_date: date of first paediatric assessment
        eligibility_criteria_met: confirmation that child is eligible for audit
        """
        # collect parameters:
        first_paediatric_assessment_date = request.POST.get(
            "first_paediatric_assessment_date"
        )
        eligibility_criteria_met = request.POST.get("eligibility_criteria_met")
        nhs_number = request.POST.get("nhs_number")
        lead_centre_id = request.POST.get("lead_centre")

        # validate those params within the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # validate parameters relating to related models
            if lead_centre_id:
                if Organisation.objects.filter(
                    ods_code=lead_centre_id, active=True
                ).exists():
                    lead_centre = Organisation.objects.get(ods_code=lead_centre_id)
                else:
                    raise serializers.ValidationError(
                        {
                            "lead_centre": f"A valid lead centre identifier must be supplied. No record saved."
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {
                        "lead_centre": f"A lead centre identifier must be supplied. No record saved."
                    }
                )

            if nhs_number:
                if Case.objects.filter(nhs_number=nhs_number).exists():
                    case = Case.objects.filter(nhs_number=nhs_number).get()
                    if Registration.objects.filter(case=case).exists():
                        raise serializers.ValidationError(
                            {
                                "nhs_number": f"{case} is already registered. No record saved."
                            }
                        )
                else:
                    raise serializers.ValidationError(
                        {
                            "nhs_number": f"{nhs_number} is not a recognised NHS Number. No record saved."
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {"nhs_number": f"Please supply an NHS Number. No record saved."}
                )

            # retrieve site allocated when case created
            try:
                site = Site.objects.filter(
                    site_is_actively_involved_in_epilepsy_care=True,
                    site_is_primary_centre_of_epilepsy_care=True,
                    case=case,
                    organisation=lead_centre,
                ).get()
            except Exception as error:
                raise serializers.ValidationError(error)

            try:
                kpi = KPI.objects.create(
                    organisation=lead_centre,
                    paediatrician_with_expertise_in_epilepsies=0,
                    epilepsy_specialist_nurse=0,
                    tertiary_input=0,
                    epilepsy_surgery_referral=0,
                    ecg=0,
                    mri=0,
                    assessment_of_mental_health_issues=0,
                    mental_health_support=0,
                    sodium_valproate=0,
                    comprehensive_care_planning_agreement=0,
                    patient_held_individualised_epilepsy_document=0,
                    patient_carer_parent_agreement_to_the_care_planning=0,
                    care_planning_has_been_updated_when_necessary=0,
                    comprehensive_care_planning_content=0,
                    parental_prolonged_seizures_care_plan=0,
                    water_safety=0,
                    first_aid=0,
                    general_participation_and_risk=0,
                    service_contact_details=0,
                    sudep=0,
                    school_individual_healthcare_plan=0,
                )
            except Exception as error:
                raise serializers.ValidationError(error)

            # update AuditProgress
            try:
                audit_progress = AuditProgress.objects.create(
                    registration_complete=True,
                    registration_total_expected_fields=3,
                    registration_total_completed_fields=3,
                )
            except Exception as error:
                # delete the site instance as some error
                site.delete()
                raise serializers.ValidationError(error)

            # create registration
            try:
                registration = Registration.objects.create(
                    case=case,
                    first_paediatric_assessment_date=datetime.strptime(
                        first_paediatric_assessment_date, "%Y-%m-%d"
                    ).date(),
                    eligibility_criteria_met=eligibility_criteria_met,
                    audit_progress=audit_progress,
                    kpi=kpi,
                )
            except Exception as error:
                site.delete()
                audit_progress.delete()
                raise serializers.ValidationError(error)

            try:
                FirstPaediatricAssessment.objects.create(registration=registration)
                EpilepsyContext.objects.create(registration=registration)
                MultiaxialDiagnosis.objects.create(registration=registration)
                Assessment.objects.create(registration=registration)
                Management.objects.create(registration=registration)
                Investigations.objects.create(registration=registration)
            except Exception as error:
                registration.delete()
                site.delete()
                audit_progress.delete()
                raise serializers.ValidationError(error)

            return Response(
                {
                    "status": "success",
                    "data": RegistrationSerializer(
                        instance=registration, context={"request": request}
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
