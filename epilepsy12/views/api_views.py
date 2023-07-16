# """
# Django Rest Framework Viewsets
# """
# # python
# # django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

# # third party
from django_filters.rest_framework import DjangoFilterBackend
from epilepsy12.serializers import *
from epilepsy12.permissions import CanAccessOrganisation


class Epilepsy12UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = Epilepsy12User.objects.all().order_by("-surname")
    serializer_class = Epilepsy12UserSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class CaseViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = Case.objects.all().order_by("-surname")
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ["nhs_number", "surname"]
    search_fields = ["=nhs_number", "^surname"]
    ordering = ["surname"]
    lookup_field = "ods_code"

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def create_case_in_organisation(self, request):
        # params
        nhs_number = request.POST.get("nhs_number")
        odsCode = request.POST.get("ODSCode")
        case_params = {
            "nhs_number": request.POST.get("nhs_number"),
            "first_name": request.POST.get("first_name"),
            "surname": request.POST.get("surname"),
            "date_of_birth": request.POST.get("date_of_birth"),
            "postcode": request.POST.get("postcode"),
            "sex": request.POST.get("sex"),
            "ethnicity": request.POST.get("ethnicity"),
        }
        if nhs_number:
            if Case.objects.filter(nhs_number=nhs_number).exists():
                case = Case.objects.filter(nhs_number=nhs_number).get()
                serializer = self.serializer_class()
                raise serializer.ValidationError(
                    {"Case": f"{case} already exists. No record created."}
                )
            else:
                serializer = self.serializer_class(data=case_params)

                if odsCode:
                    if serializer.is_valid(raise_exception=True):
                        if Organisation.objects.filter(
                            ODSCode=request.POST.get("ODSCode")
                        ).exists():
                            organisation = Organisation.objects.filter(
                                ODSCode=request.POST.get("ODSCode")
                            ).get()
                        else:
                            raise serializers.ValidationError(
                                {
                                    "Case": f"Organisation {odsCode} does not exist. No record saved."
                                }
                            )

                        try:
                            case = Case.objects.create(**case_params)
                        except Exception as error:
                            raise serializers.ValidationError({"Case": error})

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
                        {"Case": f"ODS Code Not supplied. No record created."}
                    )
        else:
            raise serializers.ValidationError(
                {"Case": f"NHS number not supplied. No record created."}
            )

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows registrations in Epilepsy12 to be viewed.
    """

    queryset = Registration.objects.all().order_by("-registration_date")
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
                if Organisation.objects.filter(ODSCode=lead_centre_id).exists():
                    lead_centre = Organisation.objects.get(ODSCode=lead_centre_id)
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
                    parent_trust=lead_centre.ParentOrganisation_OrganisationName,
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
                    registration_date=datetime.strptime(
                        registration_date, "%Y-%m-%d"
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


class FirstPaediatricAssessmentViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows details relating to the first paediatric assessment to be viewed.
    """

    queryset = FirstPaediatricAssessment.objects.all()
    serializer_class = FirstPaediatricAssessmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanAccessOrganisation,
    ]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve first paediatric assessment fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "firstpaediatricassessment"):
                instance = case.registration.firstpaediatricassessment
                serializer = FirstPaediatricAssessmentSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, nhs_number=None):
        """
        Update first paediatric assessment fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "firstpaediatricassessment"):
                instance = case.registration.firstpaediatricassessment
                serializer = FirstPaediatricAssessmentSerializer(
                    instance=instance, data=request.data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EpilepsyContextViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows children's epilepsy risk factors to be viewed.
    """

    queryset = EpilepsyContext.objects.all()
    serializer_class = EpilepsyContextSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve epilepsy context fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "epilepsycontext"):
                instance = EpilepsyContext.objects.get(
                    pk=case.registration.epilepsycontext.pk
                )
                serializer = EpilepsyContextSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update epilepsy context fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "epilepsycontext"):
                instance = EpilepsyContext.objects.get(
                    pk=case.registration.epilepsycontext.pk
                )
                serializer = EpilepsyContextSerializer(
                    instance=instance, data=request.data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MultiaxialDiagnosisViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows a multiaxial diagnosis of the child's epilepsy to be viewed.
    """

    queryset = MultiaxialDiagnosis.objects.all()
    serializer_class = MultiaxialDiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                instance = MultiaxialDiagnosis.objects.get(
                    pk=case.registration.multiaxialdiagnosis.pk
                )
                serializer = MultiaxialDiagnosisSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        Epilepy cause is passed in as a SNOMED-CT code (sctid)
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                instance = MultiaxialDiagnosis.objects.get(
                    pk=case.registration.multiaxialdiagnosis.pk
                )

                # this is a custom field passed in as a param
                # it is validated and converted to an EpilepsyCauseEntity object in the serializer
                data = {"sctid": request.data.get("sctid")}

                serializer = MultiaxialDiagnosisSerializer(
                    instance=instance, data=request.data, context=data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EpisodeViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows each seizure episode to be viewed.
    """

    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "episode"):
                    instance = Episode.objects.filter(
                        multiaxialdiagnosis=case.registration.multiaxialdiagnosis
                    )
                    serializer = EpisodeSerializer(instance=instance)
                    return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                instance = MultiaxialDiagnosis.objects.get(
                    pk=case.registration.multiaxialdiagnosis.pk
                )
                serializer = MultiaxialDiagnosisSerializer(
                    instance=instance, data=request.data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SyndromeViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows each syndrome to be viewed.
    """

    queryset = Syndrome.objects.all()
    serializer_class = SyndromeSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "syndrome"):
                    instance = Syndrome.objects.filter(
                        multiaxialdiagnosis=case.registration.multiaxialdiagnosis
                    )
                    serializer = SyndromeSerializer(instance=instance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {f"{case} has no valid syndromes documented yet."},
                        status=status.HTTP_200_OK,
                    )
        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "syndrome"):
                    instance = Syndrome.objects.get(
                        multiaxial_diagnosis=case.registration.multiaxialdiagnosis.pk
                    )
                    serializer = Syndrome(instance=instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def create(self, request, nhs_number=None):
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                serializer = Syndrome(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ComorbidityViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    """
    API endpoint that allows each comorbidity to be viewed.
    """

    queryset = Comorbidity.objects.all()
    serializer_class = ComorbiditySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "comorbidity"):
                    instance = Comorbidity.objects.filter(
                        multiaxialdiagnosis=case.registration.multiaxialdiagnosis
                    )
                    serializer = ComorbiditySerializer(instance=instance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {f"{case} has no valid comorbidities documented yet."},
                        status=status.HTTP_200_OK,
                    )
        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update multiaxial diagnosis fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                if hasattr(case.registration.multiaxialdiagnosis, "comorbidity"):
                    instance = Syndrome.objects.get(
                        multiaxial_diagnosis=case.registration.multiaxialdiagnosis.pk
                    )
                    serializer = Comorbidity(instance=instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def create(self, request):
        if "nhs_number" not in request.data:
            raise serializers.ValidationError(
                {"create comorbidity": "NHS number not supplied."}
            )
        try:
            case = Case.objects.filter(nhs_number=request.data.get("nhs_number")).get()
        except Case.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "create comorbidity": "NHS number not associated with a case registered to E12."
                }
            )
        if hasattr(case, "registration"):
            if hasattr(case.registration, "multiaxialdiagnosis"):
                serializer = ComorbiditySerializer(
                    data=request.data,
                    context={
                        "nhs_number": request.data["nhs_number"],
                        "comorbidityentity_sctid": request.data[
                            "comorbidityentity_sctid"
                        ],
                    },
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {
                    f"{case} does not have a valid multiaxial diagnosis record to register a comorbidity against."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class InvestigationsViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows a panel of investigations for each registration to be viewed.
    """

    queryset = Investigations.objects.all()
    serializer_class = InvestigationsSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve investigations fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "investigations"):
                instance = Investigations.objects.filter(
                    pk=case.registration.investigations.pk
                ).get()
                serializer = InvestigationsSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update investigations fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "investigations"):
                instance = Investigations.objects.get(
                    pk=case.registration.investigations.pk
                )
                serializer = InvestigationsSerializer(
                    instance=instance, data=request.data
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssessmentViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows key Epilepsy12 milestones to be viewed.
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"


class ManagementViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows management plans (including medications and individualised care plans) to be viewed.
    """

    queryset = Management.objects.all()
    serializer_class = ManagementSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "nhs_number"

    def retrieve(self, request, nhs_number=None):
        """
        Retrieve management fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "management"):
                instance = Management.objects.filter(
                    pk=case.registration.management.pk
                ).get()
                serializer = ManagementSerializer(instance=instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, nhs_number=None):
        """
        Update management fields by NHS number
        """
        case = get_object_or_404(Case.objects.all(), nhs_number=nhs_number)
        if hasattr(case, "registration"):
            if hasattr(case.registration, "management"):
                instance = Management.objects.get(pk=case.registration.management.pk)
                serializer = ManagementSerializer(instance=instance, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {f"{case} is invalid or not yet registered on Epilepsy12"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AntiEpilepsyMedicineViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows antiseizure medicines to be viewed.
    """

    queryset = AntiEpilepsyMedicine.objects.all()
    serializer_class = AntiEpilepsyMedicineSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class SiteViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    API endpoint that allows allocated sites to be viewed.
    """

    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a list of organisation and community trusts to be viewed.
    """

    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
    lookup_field = "ODSCode"

    def retrieve(self, request, ODSCode=None):
        """
        API endpoint that retrieves an organisation by ODS Code
        """
        queryset = Organisation.objects.all()
        organisation = get_object_or_404(queryset, ODSCode=ODSCode)
        self.check_object_permissions(self.request, organisation)
        serializer = OrganisationSerializer(organisation)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        lookup_field="ODSCode",
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def cases(self, request, ODSCode=None):
        """
        API endpoint that allows a list of all cases associated with a given organisation (retrieved by ODS Code)
        """
        queryset = Organisation.objects.all()
        organisation = get_object_or_404(queryset, ODSCode=ODSCode)
        serializer = OrganisationCaseSerializer(organisation)
        return Response(serializer.data)


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows epilepsy semiology keywords to be viewed.
    """

    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class AuditProgressViewSet(
    GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API endpoint that allows a child's progress through audit completion to be viewed.
    """

    queryset = AuditProgress.objects.all()
    serializer_class = AuditProgressSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class EpilepsyCauseEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable epilepsy causes to be viewed.
    """

    queryset = EpilepsyCauseEntity.objects.all()
    serializer_class = EpilepsyCauseEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class SyndromeEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable syndromes to be viewed.
    """

    queryset = SyndromeEntity.objects.all()
    serializer_class = SyndromeEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]


class ComorbidityEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows all selectable syndromes to be viewed.
    """

    queryset = ComorbidityEntity.objects.all()
    serializer_class = ComorbidityEntitySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessOrganisation]
