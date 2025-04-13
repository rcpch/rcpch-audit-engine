"""
Django Rest Framework Case Viewset
"""

# python

# django rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers

# third party
from django_filters.rest_framework import DjangoFilterBackend

# epilepsy12
from epilepsy12.serializers.case_serializer import CaseSerializer
from epilepsy12.serializers.first_paediatric_assessment_serializer import (
    FirstPaediatricAssessmentSerializer,
)
from epilepsy12.serializers.epilepsy_context_serializer import EpilepsyContextSerializer
from epilepsy12.serializers.investigations_serializer import InvestigationsSerializer
from epilepsy12.serializers.management_serializer import ManagementSerializer
from epilepsy12.serializers.episode_serializer import EpisodeSerializer
from epilepsy12.serializers.multiaxial_diagnosis_serializer import (
    MultiaxialDiagnosisSerializer,
)
from epilepsy12.serializers.comorbidity_serializer import ComorbiditySerializer
from epilepsy12.serializers.assessment_serializer import AssessmentSerializer
from epilepsy12.serializers.syndrome_serializer import SyndromeSerializer
from epilepsy12.models import (
    Case,
    Organisation,
    Site,
    Episode,
    MultiaxialDiagnosis,
    Comorbidity,
    Syndrome,
)
from epilepsy12.permissions import CanAccessOrganisation


class CaseViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
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
    lookup_field = "nhs_number"

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def create_case_in_organisation(self, request):
        # params
        nhs_number = request.POST.get("nhs_number")
        odsCode = request.POST.get("ods_code")
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
                            ods_code=request.POST.get("ods_code"), active=True
                        ).exists():
                            organisation = Organisation.objects.filter(
                                ods_code=request.POST.get("ods_code"), active=True
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

    def retrieve(self, request, nhs_number=None):
        return Response(
            CaseSerializer(instance=Case.objects.get(nhs_number=nhs_number)).data,
            status=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        return Response(
            CaseSerializer(Case.objects.all(), many=True).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["put", "get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def first_paediatric_assessment(self, request, nhs_number=None):
        case = Case.objects.get(nhs_number=nhs_number)

        if self.request.method == "PUT":
            serializer = FirstPaediatricAssessmentSerializer(
                case.registration.firstpaediatricassessment, request.data
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "data": FirstPaediatricAssessmentSerializer(
                            instance=case.registration.firstpaediatricassessment,
                            context={"request": request},
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                raise serializers.ValidationError(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        elif self.request.method == "GET":
            return Response(
                FirstPaediatricAssessmentSerializer(
                    instance=case.registration.firstpaediatricassessment,
                ).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise serializers.ValidationError(
                {"First paediatric assessment": "POST and PATCH requests not allowed"}
            )

    @action(
        detail=True,
        methods=["put", "get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def epilepsy_context(self, request, nhs_number=None):
        case = Case.objects.get(nhs_number=nhs_number)
        if self.request.method == "PUT":
            serializer = EpilepsyContextSerializer(
                case.registration.epilepsycontext, request.data
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "data": EpilepsyContextSerializer(
                            instance=case.registration.epilepsycontext,
                            context={"request": request},
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                raise serializers.ValidationError(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        elif self.request.method == "GET":
            return Response(
                EpilepsyContextSerializer(
                    instance=case.registration.epilepsycontext
                ).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise serializers.ValidationError(
                {"epilepsy_context": "POST and PATCH requests not allowed"}
            )

    @action(
        detail=True,
        methods=["put", "get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def investigations(self, request, nhs_number=None):
        case = Case.objects.get(nhs_number=nhs_number)
        if self.request.method == "PUT":
            serializer = InvestigationsSerializer(
                case.registration.investigations, request.data
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "data": InvestigationsSerializer(
                            instance=case.registration.investigations,
                            context={"request": request},
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                raise serializers.ValidationError(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        elif self.request.method == "GET":
            return Response(
                InvestigationsSerializer(
                    instance=case.registration.investigations
                ).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise serializers.ValidationError(
                {"investigations": "POST and PATCH requests not allowed"}
            )

    @action(
        detail=True,
        methods=["put", "get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def management(self, request, nhs_number=None):
        case = Case.objects.get(nhs_number=nhs_number)
        if self.request.method == "PUT":
            serializer = ManagementSerializer(
                case.registration.management, request.data
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "data": ManagementSerializer(
                            instance=case.registration.management,
                            context={"request": request},
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                raise serializers.ValidationError(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        elif self.request.method == "GET":
            return Response(
                ManagementSerializer(instance=case.registration.management).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise serializers.ValidationError(
                {"Management": "POST and PATCH requests not allowed"}
            )

    @action(
        detail=True,
        methods=["put", "get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def assessment(self, request, nhs_number=None):
        case = Case.objects.get(nhs_number=nhs_number)
        if self.request.method == "PUT":
            context = {
                "general_paediatric_centre_ods_code": self.request.data[
                    "general_paediatric_centre_ods_code"
                ],
                "paediatric_neurology_centre_ods_code": self.request.data[
                    "paediatric_neurology_centre_ods_code"
                ],
                "epilepsy_surgery_centre_ods_code": self.request.data[
                    "epilepsy_surgery_centre_ods_code"
                ],
            }
            serializer = AssessmentSerializer(
                case.registration.assessment, request.data, context=context
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "data": AssessmentSerializer(
                            instance=case.registration.assessment,
                            context=context,
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                raise serializers.ValidationError(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        elif self.request.method == "GET":
            return Response(
                AssessmentSerializer(instance=case.registration.assessment).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise serializers.ValidationError(
                {"Assessment": "POST and PATCH requests not allowed"}
            )

    @action(
        detail=True,
        methods=["get", "put"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def multiaxial_diagnosis(self, request, nhs_number=None):
        """
        Get or update multiaxial diagnosis instance
        """
        if nhs_number is None:
            raise serializers.ValidationError(
                {"Comorbidities": "No NHS number supplied."}
            )
        if not Case.objects.filter(nhs_number=nhs_number).exists():
            raise serializers.ValidationError(
                {
                    "Comorbidities": "No Case in Epilepsy12 is associated with the NHS number supplied."
                }
            )
        case = Case.objects.get(nhs_number=nhs_number)

        if request.method == "GET":
            return Response(
                MultiaxialDiagnosisSerializer(
                    instance=case.registration.multiaxialdiagnosis
                ).data,
                status=status.HTTP_200_OK,
            )
        elif request.method == "PUT":
            instance = MultiaxialDiagnosis.objects.get(
                pk=case.registration.multiaxialdiagnosis.pk
            )

            # this is a custom field passed in as a param
            # it is validated and converted to an Comorbidity object in the serializer
            data = {"sctid": request.data.get("sctid")}

            serializer = MultiaxialDiagnosisSerializer(
                instance=instance, data=request.data, context=data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def comorbidities(self, request, nhs_number=None):
        """
        Returns a list of comorbidities for a given Case
        """
        if nhs_number is None:
            raise serializers.ValidationError(
                {"Comorbidities": "No NHS number supplied."}
            )
        if not Case.objects.filter(nhs_number=nhs_number).exists():
            raise serializers.ValidationError(
                {
                    "Comorbidities": "No Case in Epilepsy12 is associated with the NHS number supplied."
                }
            )

        case = Case.objects.get(nhs_number=nhs_number)

        return Response(
            ComorbiditySerializer(
                instance=Comorbidity.objects.filter(
                    multiaxial_diagnosis=case.registration.multiaxialdiagnosis
                ),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def comorbidity(self, request, nhs_number=None):
        """
        create comorbidity associated with nhs number
        """
        serializer = ComorbiditySerializer(
            data=request.data,
            context={
                "nhs_number": nhs_number,
                "comorbidityentity_sctid": request.data.get(
                    "comorbidityentity_sctid", None
                ),
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def episodes(self, request, nhs_number=None):
        """
        Returns a list of episodes for a given Case
        """
        if nhs_number is None:
            raise serializers.ValidationError({"Episodes": "No NHS number supplied."})
        if not Case.objects.filter(nhs_number=nhs_number).exists():
            raise serializers.ValidationError(
                {
                    "Episodes": "No Case in Epilepsy12 is associated with the NHS number supplied."
                }
            )

        case = Case.objects.get(nhs_number=nhs_number)

        return Response(
            EpisodeSerializer(
                instance=Episode.objects.filter(
                    multiaxial_diagnosis=case.registration.multiaxialdiagnosis
                ),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def episode(self, request, nhs_number=None):
        """
        create episode associated with nhs number
        """
        serializer = EpisodeSerializer(
            data=request.data,
            context={
                "nhs_number": nhs_number,
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def syndromes(self, request, nhs_number=None):
        """
        Returns a list of syndromes for a given Case
        """
        if nhs_number is None:
            raise serializers.ValidationError({"Syndromes": "No NHS number supplied."})
        if not Case.objects.filter(nhs_number=nhs_number).exists():
            raise serializers.ValidationError(
                {
                    "Syndromes": "No Case in Epilepsy12 is associated with the NHS number supplied."
                }
            )

        case = Case.objects.get(nhs_number=nhs_number)

        return Response(
            SyndromeSerializer(
                instance=Syndrome.objects.filter(
                    multiaxial_diagnosis=case.registration.multiaxialdiagnosis
                ),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanAccessOrganisation],
    )
    def syndrome(self, request, nhs_number=None):
        """
        create Syndrome associated with nhs number
        """
        serializer = SyndromeSerializer(
            data=request.data,
            context={
                "nhs_number": nhs_number,
                "syndrome_name": request.data.get("syndrome_name", None),
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
