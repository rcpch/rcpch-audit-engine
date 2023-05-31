"""
Measure 8 - Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

- [ ] Measure 8 passed (registration.kpi.sodium_valproate == 1) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and is_a_pregnancy_prevention_programme_needed==True and has_a_valproate_annual_risk_acknowledgement_form_been_completed==True
- [ ] Measure 8 failed (registration.kpi.sodium_valproate == 0) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and is_a_pregnancy_prevention_programme_needed is False or None
- [ ] Measure 8 failed (registration.kpi.sodium_valproate == 0) if (age_at_first_paediatric_assessment >= 12 and sex == 2 and medicine is valproate) and has_a_valproate_annual_risk_acknowledgement_form_been_completed is False or None

- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if age_at_first_paediatric_assessment < 12
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if registration_instance.case.sex == 1
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if registration_instance.management.has_an_aed_been_given == False
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if AEM is not valproate or AEM is None

    # calculate age_at_first_paediatric_assessment
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.registration_date,
        registration_instance.case.date_of_birth,
    ).years

        if (
            age_at_first_paediatric_assessment >= 12
            and registration_instance.case.sex == 2
        ) and (
            registration_instance.management.has_an_aed_been_given
            and AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                medicine_entity=MedicineEntity.objects.filter(
                    medicine_name__icontains="valproate"
                ).first(),
            ).exists()
        ):
            # eligible for this measure
            sodium_valproate = 0
            if (
                age_at_first_paediatric_assessment >= 12
                and registration_instance.case.sex == 2
            ) and (
                registration_instance.management.has_an_aed_been_given
                and AntiEpilepsyMedicine.objects.filter(
                    management=registration_instance.management,
                    medicine_entity=MedicineEntity.objects.filter(
                        medicine_name__icontains="valproate"
                    ).first(),
                    is_a_pregnancy_prevention_programme_needed=True,
                    has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
                ).exists()
            ):
                # criteria met
                sodium_valproate = 1
        else:
            # not eligible for this measure
            sodium_valproate = 2
"""
