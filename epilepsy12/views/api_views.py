# """
# Django Rest Framework Viewsets
# """
# # python

# # django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions, viewsets

# # third party
from epilepsy12.serializers import *


class Epilepsy12UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Epilepsy12User.objects.all().order_by("-surname")
    serializer_class = Epilepsy12UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Case.objects.all().order_by("-surname")
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add_case_to_organisation_list(self, request):
        # params
        nhs_number = request.POST.get("nhs_number")
        organisationID = request.POST.get("OrganisationID")
        case_params = {
            "nhs_number": request.POST.get("nhs_number"),
            "first_name": request.POST.get("first_name"),
            "surname": request.POST.get("surname"),
            "date_of_birth": request.POST.get("date_of_birth"),
            "sex": request.POST.get("sex"),
            "ethnicity": request.POST.get("ethnicity"),
        }
        if nhs_number:
            if Case.objects.filter(nhs_number=nhs_number).exists():
                case = Case.objects.filter(nhs_number=nhs_number).get()
                raise serializers.ValidationError(
                    {"Case": f"{case} already exists. No record created."}
                )
            else:
                serializer = self.serializer(data=case_params)

                if organisationID:
                    if serializer.is_valid(raise_exception=True):
                        if Organisation.objects.filter(
                            OrganisationID=request.POST.get("OrganisationID")
                        ).exists():
                            organisation = Organisation.objects.filter(
                                OrganisationID=request.POST.get("OrganisationID")
                            ).get()
                        else:
                            raise serializers.ValidationError(
                                {
                                    "Case": f"Organisation {organisationID} does not exist. No record saved."
                                }
                            )

                        try:
                            case = Case.objects.create(**case_params)
                        except Exception as error:
                            raise serializers.ValidationError({"Case": error})

                        print(f"{case} created")

                        try:
                            Site.objects.create(
                                case=case,
                                organisation=organisation,
                                site_is_actively_involved_in_epilepsy_care=True,
                                site_is_primary_centre_of_epilepsy_care=True,
                            )
                        except Exception as error:
                            case.delete()
                            raise serializers.ValidationError({"Case": error})

                        return Response(
                            {"status": "success", "data": case_params},
                            status=status.HTTP_200_OK,
                        )

                else:
                    raise serializers.ValidationError(
                        {"Case": f"OrganisationID Not supplied. No record created."}
                    )
        else:
            raise serializers.ValidationError(
                {"Case": f"NHS number not supplied. No record created."}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows registrations in Epilepsy12 to be viewed or edited.
    """

    queryset = Registration.objects.all().order_by("-registration_date")
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def register_case(self, request):
        """
        Create an active registration in the audit.
        Essential parameters:
        nhs_number: 10 digit number
        lead_centre: OrganisationID
        registration_date: date of first paediatric assessment
        eligibility_criteria_met: confirmation that child is eligible for audit
        """
        # collect parameters:
        registration_date = request.POST.get("registration_date")
        eligibility_criteria_met = request.POST.get("eligibility_criteria_met")
        nhs_number = request.POST.get("nhs_number")
        lead_centre_id = request.POST.get("lead_centre")

        # validate those params within the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # validate parameters relating to related models
            if lead_centre_id:
                if Organisation.objects.filter(OrganisationID=lead_centre_id).exists():
                    lead_centre = Organisation.objects.get(
                        OrganisationID=lead_centre_id
                    )
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

            # create site
            try:
                site = Site.objects.create(
                    site_is_actively_involved_in_epilepsy_care=True,
                    site_is_primary_centre_of_epilepsy_care=True,
                    case=case,
                    organisation=lead_centre,
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
                    registration_date=datetime.strptime(
                        registration_date, "%Y-%m-%d"
                    ).date(),
                    eligibility_criteria_met=eligibility_criteria_met,
                    audit_progress=audit_progress,
                )
            except Exception as error:
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


class FirstPaediatricAssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows details relating to the first paediatric assessment to be viewed or edited.
    """

    queryset = FirstPaediatricAssessment.objects.all()
    serializer_class = FirstPaediatricAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EpilepsyContextViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows children's epilepsy risk factors to be viewed or edited.
    """

    queryset = EpilepsyContext.objects.all()
    serializer_class = EpilepsyContextSerializer
    permission_classes = [permissions.IsAuthenticated]


class MultiaxialDiagnosisViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a multiaxial diagnosis of the child's epilepsy to be viewed or edited.
    """

    queryset = MultiaxialDiagnosis.objects.all()
    serializer_class = MultiaxialDiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]


class EpisodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each seizure episode to be viewed or edited.
    """

    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SyndromeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each syndrome to be viewed or edited.
    """

    queryset = Syndrome.objects.all()
    serializer_class = SyndromeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ComorbidityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each comorbidity to be viewed or edited.
    """

    queryset = Comorbidity.objects.all()
    serializer_class = ComorbiditySerializer
    permission_classes = [permissions.IsAuthenticated]


class InvestigationsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a panel of investigations for each registration to be viewed or edited.
    """

    queryset = Investigations.objects.all()
    serializer_class = InvestigationsSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows key Epilepsy12 milestones to be viewed or edited.
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManagementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows management plans (including medications and individualised care plans) to be viewed or edited.
    """

    queryset = Management.objects.all()
    serializer_class = ManagementSerializer
    permission_classes = [permissions.IsAuthenticated]


class AntiEpilepsyMedicineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows antiseizure medicines to be viewed or edited.
    """

    queryset = AntiEpilepsyMedicine.objects.all()
    serializer_class = AntiEpilepsyMedicineSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows allocated sites to be viewed or edited.
    """

    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a list of organisation and community trusts to be viewed or edited.
    """

    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]


class KeywordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows epilepsy semiology keywords to be viewed or edited.
    """

    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a child's progress through audit completion to be viewed or edited.
    """

    queryset = AuditProgress.objects.all()
    serializer_class = AuditProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
