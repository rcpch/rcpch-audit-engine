# Python imports

# Django imports

# DRF imports
from rest_framework import serializers

# E12 imports
from epilepsy12.models import MultiaxialDiagnosis, Comorbidity, ComorbidityEntity, Case
from epilepsy12.common_view_functions import update_audit_progress, calculate_kpis


class ComorbiditySerializer(serializers.ModelSerializer):
    comorbidityentity = serializers.SlugRelatedField(
        read_only=True, slug_field="preferredTerm"
    )

    class Meta:
        model = Comorbidity
        multiaxial_diagnosis = serializers.PrimaryKeyRelatedField(
            queryset=MultiaxialDiagnosis.objects.all()
        )
        fields = ("id", "comorbidityentity", "comorbidity_diagnosis_date")

    def validate(self, data):
        if (
            "comorbidityentity_sctid" not in self.context
            or self.context.get("comorbidityentity_sctid") is None
        ):
            raise serializers.ValidationError(
                {"comorbidity": "ComorbidityEntity SNOMED code not supplied!"}
            )

        if "comorbidity_diagnosis_date" not in data:
            raise serializers.ValidationError(
                {"comorbidity": "Date of comorbidity diagnosis not supplied!"}
            )

        return data

    def update(self, instance, validated_data):
        instance.comorbidity_diagnosis_date = validated_data.get(
            "comorbidity_diagnosis_date", instance.comorbidity_diagnosis_date
        )
        comorbidityentity = ComorbidityEntity.objects.filter(
            conceptId=self.context.get("comorbidityentity_sctid")
        ).first()
        instance.comorbidityentity = comorbidityentity
        # instance.multiaxial_diagnosis = validated_data(
        #     "multiaxial_diagnosis", instance.multiaxial_diagnosis
        # )

        instance.save()

        # set RIBE to true
        multiaxial_diagnosis = instance.multiaxial_diagnosis
        multiaxial_diagnosis.relevant_impairments_behavioural_educational = True
        multiaxial_diagnosis.save()

        update_audit_progress(multiaxial_diagnosis.registration)
        calculate_kpis(multiaxial_diagnosis.registration)
        return instance

    def create(self, validated_data):
        if (
            ComorbidityEntity.objects.filter(
                conceptId=self.context.get("comorbidityentity_sctid")
            ).count()
            < 1
        ):
            raise serializers.ValidationError(
                {
                    "create comorbidity": "SNOMED CT id supplied invalid or not in Epilepsy12 refset."
                }
            )
        else:
            comorbidityentity = ComorbidityEntity.objects.filter(
                conceptId=self.context.get("comorbidityentity_sctid")
            ).first()
            nhs_number = self.context.get("nhs_number")
            try:
                case = Case.objects.get(nhs_number=nhs_number)
            except Exception as error:
                raise serializers.ValidationError({"create comorbidity": error})
            instance = Comorbidity.objects.create(
                multiaxial_diagnosis=case.registration.multiaxialdiagnosis,
                comorbidityentity=comorbidityentity,
                comorbidity_diagnosis_date=validated_data["comorbidity_diagnosis_date"],
            )
            # set RIBE to true
            multiaxial_diagnosis = case.registration.multiaxialdiagnosis
            multiaxial_diagnosis.relevant_impairments_behavioural_educational = True
            multiaxial_diagnosis.save()

            update_audit_progress(case.registration)
            calculate_kpis(case.registration)
            return instance
