from django.apps import apps
from django.contrib.gis.db import models
from .help_text_mixin import HelpTextMixin

# ---------------------------------------------------------------------------
# Module-level constants used by AuditProgress completeness methods
# ---------------------------------------------------------------------------

# Fields present on every model via the abstract base classes; never scored.
_AUDIT_BASE_EXCLUDE = frozenset(
    {
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "history",
    }
)

# All non-epileptic subtype fields on Episode.
_NONEPILEPTIC_EPISODE_FIELDS = frozenset(
    {
        "nonepileptic_seizure_type",
        "nonepileptic_seizure_unknown_onset",
        "nonepileptic_seizure_syncope",
        "nonepileptic_seizure_behavioural",
        "nonepileptic_seizure_sleep",
        "nonepileptic_seizure_paroxysmal",
        "nonepileptic_seizure_migraine",
        "nonepileptic_seizure_miscellaneous",
        "nonepileptic_seizure_other",
    }
)

# Focal-onset feature checkboxes — optional, only laterality is required.
_FOCAL_FEATURE_FIELDS = frozenset(
    {
        "focal_onset_impaired_awareness",
        "focal_onset_automatisms",
        "focal_onset_atonic",
        "focal_onset_clonic",
        "focal_onset_epileptic_spasms",
        "focal_onset_hyperkinetic",
        "focal_onset_myoclonic",
        "focal_onset_tonic",
        "focal_onset_autonomic",
        "focal_onset_behavioural_arrest",
        "focal_onset_cognitive",
        "focal_onset_emotional",
        "focal_onset_sensory",
        "focal_onset_centrotemporal",
        "focal_onset_temporal",
        "focal_onset_frontal",
        "focal_onset_parietal",
        "focal_onset_occipital",
        "focal_onset_gelastic",
        "focal_onset_focal_to_bilateral_tonic_clonic",
    }
)

# Focal-laterality fields — at least one must be set for a focal episode.
_FOCAL_LATERALITY_FIELDS = frozenset(
    {
        "focal_onset_left",
        "focal_onset_right",
        "focal_onset_laterality_unknown",
    }
)

_ALL_FOCAL_FIELDS = _FOCAL_FEATURE_FIELDS | _FOCAL_LATERALITY_FIELDS

# Maps nonepileptic_seizure_type choice value → the relevant subtype field.
_NONEPILEPTIC_SUBTYPE_FIELD = {
    "SAS": "nonepileptic_seizure_syncope",
    "BPP": "nonepileptic_seizure_behavioural",
    "SRC": "nonepileptic_seizure_sleep",
    "PMD": "nonepileptic_seizure_paroxysmal",
    "MAD": "nonepileptic_seizure_migraine",
    "ME": "nonepileptic_seizure_miscellaneous",
    "Oth": "nonepileptic_seizure_other",
}

# SNOMED concept IDs used for KPI-8 medication logic.
_SODIUM_VALPROATE_CONCEPT_ID = "387481005"
_TOPIRAMATE_CONCEPT_ID = "777808008"


class AuditProgress(models.Model, HelpTextMixin):
    """
    A record is created in the AuditProgress class every time a case is registered for the audit
    It tracks how many fields are complete
    """

    registration_complete = models.BooleanField(default=False, null=True)
    registration_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    registration_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    first_paediatric_assessment_complete = models.BooleanField(default=False, null=True)
    first_paediatric_assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    first_paediatric_assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    assessment_complete = models.BooleanField(null=True, default=False)
    assessment_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    assessment_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    epilepsy_context_complete = models.BooleanField(null=True, default=False)
    epilepsy_context_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    epilepsy_context_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    multiaxial_diagnosis_complete = models.BooleanField(null=True, default=False)
    multiaxial_diagnosis_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    multiaxial_diagnosis_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    investigations_complete = models.BooleanField(default=False, null=True)
    investigations_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    investigations_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )
    management_complete = models.BooleanField(default=False, null=True)
    management_total_expected_fields = models.SmallIntegerField(
        "Total Number of fields expected", default=0, null=True
    )
    management_total_completed_fields = models.SmallIntegerField(
        "Total Number of fields completed", default=0, null=True
    )

    consent_patient_confirmed = models.BooleanField(default=None, null=True)

    details_patient_confirmed = models.BooleanField(default=None, null=True)

    """
    Calculated fields
    """

    @property
    def total_completed_fields(self):
        total_fields = 0
        if self.registration_total_completed_fields:
            total_fields += self.registration_total_completed_fields
        if self.first_paediatric_assessment_total_completed_fields:
            total_fields += self.first_paediatric_assessment_total_completed_fields
        if self.assessment_total_completed_fields:
            total_fields += self.assessment_total_completed_fields
        if self.epilepsy_context_total_completed_fields:
            total_fields += self.epilepsy_context_total_completed_fields
        if self.multiaxial_diagnosis_total_completed_fields:
            total_fields += self.multiaxial_diagnosis_total_completed_fields
        if self.investigations_total_completed_fields:
            total_fields += self.investigations_total_completed_fields
        if self.management_total_completed_fields:
            total_fields += self.management_total_completed_fields
        return total_fields

    @property
    def total_expected_fields(self):
        total_fields = 0
        if self.registration_total_expected_fields:
            total_fields += self.registration_total_expected_fields
        else:
            total_fields += 3
        if self.first_paediatric_assessment_total_expected_fields:
            total_fields += self.first_paediatric_assessment_total_expected_fields
        else:
            total_fields += 6
        if self.assessment_total_expected_fields:
            total_fields += self.assessment_total_expected_fields
        else:
            total_fields += 5
        if self.epilepsy_context_total_expected_fields:
            total_fields += self.epilepsy_context_total_expected_fields
        else:
            total_fields += 8
        if self.multiaxial_diagnosis_total_expected_fields:
            total_fields += self.multiaxial_diagnosis_total_expected_fields
        else:
            total_fields += 10
        if self.investigations_total_expected_fields:
            total_fields += self.investigations_total_expected_fields
        else:
            total_fields += 4
        if self.management_total_expected_fields:
            total_fields += self.management_total_expected_fields
        else:
            total_fields += 5

        return total_fields

    @property
    def audit_complete(self):
        if (
            self.registration_complete
            and self.first_paediatric_assessment_complete
            and self.epilepsy_context_complete
            and self.assessment_complete
            and self.multiaxial_diagnosis_complete
            and self.investigations_complete
            and self.management_complete
        ):
            return True
        else:
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _field_label(self, field):
        """Return a user-facing label for a model field."""
        ht = getattr(field, "help_text", None)
        if isinstance(ht, dict):
            return ht.get("label", str(field.verbose_name))
        return str(field.verbose_name)

    def _incomplete_fields_for_instance(self, instance, extra_exclude=None):
        """
        Return a list of human-readable labels for concrete fields on
        *instance* whose value is None / "" / [].

        Uses ``_meta.fields`` (concrete columns only — no reverse relations)
        so ForeignKey reverse managers are never evaluated.
        """
        exclude = _AUDIT_BASE_EXCLUDE | (extra_exclude or frozenset())
        result = []
        for field in instance._meta.fields:
            if field.name in exclude:
                continue
            value = getattr(instance, field.name, None)
            if value in (None, "", []):
                result.append(self._field_label(field))
        return result

    def _exclude_fields_for_episode(self, episode):
        """
        Return the set of field names that should NOT be checked for
        completeness on *episode*, based on its current state.
        """
        exclude = {"expected_score", "calculated_score", "multiaxial_diagnosis"}

        # Date confidence is only asked once a date has been entered.
        if not episode.seizure_onset_date:
            exclude.add("seizure_onset_date_confidence")

        # Description fields are only shown when the clinician confirms
        # they have gathered a description.
        if not episode.has_description_of_the_episode_or_episodes_been_gathered:
            exclude.update({"description", "description_keywords"})

        status = episode.epilepsy_or_nonepilepsy_status
        onset_type = episode.epileptic_seizure_onset_type
        ne_type = episode.nonepileptic_seizure_type

        if status == "E":
            # Epileptic — hide all non-epileptic fields.
            exclude |= _NONEPILEPTIC_EPISODE_FIELDS
            # Focal feature checkboxes are optional; only laterality is scored.
            exclude |= _FOCAL_FEATURE_FIELDS
            if onset_type != "GO":
                exclude.add("epileptic_generalised_onset")
            if onset_type != "FO":
                exclude |= _FOCAL_LATERALITY_FIELDS
        elif status in ("NE", "U"):
            # Non-epileptic / uncertain — hide epileptic onset fields and
            # focal fields; unknown-onset field relevant for "U".
            exclude.update(
                {"epileptic_seizure_onset_type", "epileptic_generalised_onset"}
            )
            exclude |= _ALL_FOCAL_FIELDS
            if status == "NE":
                exclude.add("nonepileptic_seizure_unknown_onset")
            # Exclude nonepileptic subtype fields that don't match the chosen type.
            if ne_type:
                relevant = _NONEPILEPTIC_SUBTYPE_FIELD.get(ne_type)
                exclude |= {
                    f
                    for f in _NONEPILEPTIC_EPISODE_FIELDS
                    if f
                    not in (
                        "nonepileptic_seizure_type",
                        "nonepileptic_seizure_unknown_onset",
                        relevant,
                    )
                }
            else:
                # No NE type chosen yet — hide all subtype fields.
                exclude |= _NONEPILEPTIC_EPISODE_FIELDS - {"nonepileptic_seizure_type"}
        else:
            # Status not yet set — hide every conditional field.
            exclude |= _NONEPILEPTIC_EPISODE_FIELDS
            exclude |= _ALL_FOCAL_FIELDS
            exclude.update(
                {"epileptic_seizure_onset_type", "epileptic_generalised_onset"}
            )

        return exclude

    def _exclude_fields_for_aem(self, aem):
        """
        Return field names to skip when checking an AntiEpilepsyMedicine
        instance for completeness.
        """
        exclude = {"management", "medicine_entity"}
        # Stop date is optional (medicine may be ongoing).
        exclude.add("antiepilepsy_medicine_stop_date")

        # KPI-8 reproductive-risk fields are conditional by cohort, medicine,
        # age and sex (see docs/development/key-performance-indicators.md).
        try:
            registration = aem.management.registration
            case = registration.case
            cohort = registration.cohort
            sex = case.sex
            child_over_12 = case.age_days() >= 365.25 * 12
            concept_id = (
                aem.medicine_entity.conceptId
                if aem.medicine_entity is not None
                else None
            )
        except Exception:
            cohort = None
            sex = None
            child_over_12 = False
            concept_id = None

        is_valproate = concept_id == _SODIUM_VALPROATE_CONCEPT_ID
        is_topiramate = concept_id == _TOPIRAMATE_CONCEPT_ID
        is_female = sex == 2

        # Default to excluding all KPI-8 conditional fields until proven applicable.
        exclude.update(
            {
                "is_a_pregnancy_prevention_programme_needed",
                "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
                "is_a_pregnancy_prevention_programme_in_place",
            }
        )

        if cohort is None:
            return exclude

        # Cohort 6: females >= 12 on valproate require annual risk form only.
        if cohort == 6 and is_female and child_over_12 and is_valproate:
            exclude.discard(
                "has_a_valproate_annual_risk_acknowledgement_form_been_completed"
            )
            return exclude

        # Cohort 7+: females on valproate OR females >= 12 on topiramate.
        eligible_kpi8 = is_female and (
            is_valproate or (is_topiramate and child_over_12)
        )
        if cohort >= 7 and eligible_kpi8:
            exclude.discard("is_a_pregnancy_prevention_programme_needed")
            exclude.discard(
                "has_a_valproate_annual_risk_acknowledgement_form_been_completed"
            )
            # PPP in place only applies when PPP is indicated.
            if aem.is_a_pregnancy_prevention_programme_needed:
                exclude.discard("is_a_pregnancy_prevention_programme_in_place")

        return exclude

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def audit_progress_fields_incomplete(self, model_name):
        """
        Return a list of human-readable labels for incomplete fields in a
        1-to-1 model (registration, firstpaediatricassessment, epilepsycontext,
        assessment, multiaxialdiagnosis, investigations, management).

        For 1-to-many related models (episode, syndrome, comorbidity,
        antiepilepsymedicine) use ``audit_progress_related_instances_incomplete``.
        """
        try:
            root = self if model_name == "registration" else self.registration
            instance = getattr(root, model_name)
        except Exception:
            return []
        extra_exclude = frozenset(
            self.exclude_fields_from_audit_progress(model_name=model_name)
        )
        return self._incomplete_fields_for_instance(instance, extra_exclude)

    def __str__(self):
        Registration = apps.get_model("epilepsy12", "Registration")
        Site = apps.get_model("epilepsy12", "Site")
        registration = Registration.objects.filter(audit_progress=self).first()
        if registration and hasattr(registration, "case"):
            lead_site = Site.objects.get(
                case=registration.case,
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_primary_centre_of_epilepsy_care=True,
            )
            return f"Audit progress for {self.registration.case} [{lead_site.organisation}](cohort {registration.cohort})"
        else:
            return f"No AuditProgress record yet"

    class Meta:
        verbose_name = "Audit Progress"
        verbose_name_plural = "Audit Progresses"
        ordering = ["registration__case"]

    def exclude_fields_from_audit_progress(self, model_name):
        fields_to_exclude = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "audit_progress",
            "case",
        ]

        cohort = self.registration.cohort
        if model_name == "registration":
            fields_to_exclude.append("cohort")
            model_instance = getattr(self, model_name)
            if not hasattr(model_instance, "registration"):
                return fields_to_exclude
        else:
            fields_to_exclude.append("registration")

        if model_name == "investigations":
            if self.registration.investigations.mri_indicated is False:
                fields_to_exclude.append("mri_brain_requested_date")
                fields_to_exclude.append("mri_brain_reported_date")
        # elif model_name == "epilepsycontext":
        #     fields_to_exclude.append("epilepsy_context")
        elif model_name == "assessment":
            if (
                self.registration.assessment.consultant_paediatrician_referral_made
                is False
            ):
                fields_to_exclude.append("consultant_paediatrician_input_achieved")
                fields_to_exclude.append("consultant_paediatrician_referral_date")
                fields_to_exclude.append("consultant_paediatrician_input_date")
            if (
                self.registration.assessment.epilepsy_specialist_nurse_referral_made
                is False
            ):
                fields_to_exclude.append("epilepsy_specialist_nurse_referral_date")
            if (
                self.registration.assessment.epilepsy_specialist_nurse_input_achieved
                is False
            ):
                fields_to_exclude.append("epilepsy_specialist_nurse_input_date")
            if (
                self.registration.assessment.paediatric_neurologist_referral_made
                is False
            ):
                fields_to_exclude.append("paediatric_neurologist_input_achieved")
                fields_to_exclude.append("paediatric_neurologist_referral_date")
                fields_to_exclude.append("paediatric_neurologist_input_date")
            if (
                self.registration.assessment.childrens_epilepsy_surgical_service_referral_made
                is False
            ):
                fields_to_exclude.append(
                    "childrens_epilepsy_surgical_service_referral_date"
                )
                fields_to_exclude.append(
                    "childrens_epilepsy_surgical_service_input_date"
                )
        elif model_name == "multiaxialdiagnosis":
            if cohort < 8:
                fields_to_exclude.append(
                    "global_developmental_delay_or_learning_difficulties"
                )
                fields_to_exclude.append(
                    "global_developmental_delay_or_learning_difficulties_severity"
                )
                fields_to_exclude.append("autistic_spectrum_disorder")
                fields_to_exclude.append("mental_health_screen")
                fields_to_exclude.append("mental_health_issue_identified")
                fields_to_exclude.append("mental_health_issues")
            if (
                self.registration.multiaxialdiagnosis.global_developmental_delay_or_learning_difficulties
                is False
            ):
                fields_to_exclude.append(
                    "global_developmental_delay_or_learning_difficulties_severity"
                )
        else:
            model_instance = getattr(self.registration, model_name)
            cohort = self.registration.cohort
            if cohort < 8:
                fields_to_exclude.extend(
                    [
                        "registration",
                        "r14_test_status",
                        "r14_test_requested_date",
                        "r14_test_achieved_date",
                        "r27_test_status",
                        "r27_test_requested_date",
                        "r27_test_achieved_date",
                        "r59_test_status",
                        "r59_test_requested_date",
                        "r59_test_achieved_date",
                        "genome_sequencing_requested",
                        "global_developmental_delay_or_learning_difficulties_severity",
                        "mental_health_issues",
                    ]
                )
        return fields_to_exclude

    def audit_progress_related_instances_incomplete(self, related_model_name):
        """
        For 1-to-many related models, return a list of dicts describing
        which instances have incomplete fields::

            [
                {"label": "Episode 1 (01 Jan 2024)", "incomplete": ["Seizure type", ...]},
                ...
            ]

        *related_model_name* must be one of:
            "episode", "syndrome", "comorbidity", "antiepilepsymedicine"

        Returns an empty list when the queryset is empty or all instances
        are already complete.
        """
        results = []
        normalized_name = (related_model_name or "").strip().lower()
        alias_map = {
            "episodes": "episode",
            "syndromes": "syndrome",
            "comorbidities": "comorbidity",
            "antiepilepsymedicines": "antiepilepsymedicine",
            "epilepsycause": "epilepsycause",
        }
        normalized_name = alias_map.get(normalized_name, normalized_name)

        if normalized_name == "episode":
            try:
                queryset = self.registration.multiaxialdiagnosis.episodes.all()
            except Exception:
                return []
            if not queryset.exists():
                results.append(
                    {
                        "label": "Episodes",
                        "incomplete": ["Add at least one episode"],
                    }
                )
                return results
            for i, episode in enumerate(queryset, start=1):
                label = f"Episode {i}"
                if episode.seizure_onset_date:
                    label += f" ({episode.seizure_onset_date.strftime('%d %b %Y')})"
                extra_exclude = self._exclude_fields_for_episode(episode)
                incomplete = self._incomplete_fields_for_instance(
                    episode, extra_exclude
                )
                if incomplete:
                    results.append({"label": label, "incomplete": incomplete})

        elif normalized_name == "syndrome":
            try:
                multiaxial = self.registration.multiaxialdiagnosis
                queryset = multiaxial.syndromes.all()
            except Exception:
                return []
            if multiaxial.syndrome_present is True and not queryset.exists():
                results.append(
                    {
                        "label": "Syndromes",
                        "incomplete": ["Add at least one syndrome"],
                    }
                )
                return results
            for i, syndrome in enumerate(queryset, start=1):
                label = str(syndrome.syndrome) if syndrome.syndrome else f"Syndrome {i}"
                extra_exclude = frozenset({"multiaxial_diagnosis"})
                incomplete = self._incomplete_fields_for_instance(
                    syndrome, extra_exclude
                )
                if incomplete:
                    results.append({"label": label, "incomplete": incomplete})

        elif normalized_name == "comorbidity":
            try:
                multiaxial = self.registration.multiaxialdiagnosis
                queryset = multiaxial.comorbidities.all()
            except Exception:
                return []
            if (
                multiaxial.relevant_impairments_behavioural_educational is True
                and not queryset.exists()
            ):
                results.append(
                    {
                        "label": "Comorbidities",
                        "incomplete": ["Add at least one comorbidity"],
                    }
                )
                return results
            for i, comorbidity in enumerate(queryset, start=1):
                label = (
                    str(comorbidity.comorbidityentity)
                    if comorbidity.comorbidityentity
                    else f"Comorbidity {i}"
                )
                # comorbidityentity is always set before saving; exclude from check.
                extra_exclude = frozenset({"multiaxial_diagnosis", "comorbidityentity"})
                incomplete = self._incomplete_fields_for_instance(
                    comorbidity, extra_exclude
                )
                if incomplete:
                    results.append({"label": label, "incomplete": incomplete})

        elif normalized_name == "antiepilepsymedicine":
            try:
                management = self.registration.management
                queryset = management.antiepilepsymedicine_set.all()
            except Exception:
                return []
            if management.has_an_aed_been_given is True and not queryset.exists():
                results.append(
                    {
                        "label": "Antiseizure medicines",
                        "incomplete": ["Add at least one antiseizure medicine"],
                    }
                )
                return results
            for i, aem in enumerate(queryset, start=1):
                label = (
                    str(aem.medicine_entity) if aem.medicine_entity else f"Medicine {i}"
                )
                extra_exclude = self._exclude_fields_for_aem(aem)
                incomplete = self._incomplete_fields_for_instance(aem, extra_exclude)
                if incomplete:
                    results.append({"label": label, "incomplete": incomplete})

        elif normalized_name == "epilepsycause":
            try:
                multiaxial = self.registration.multiaxialdiagnosis
            except Exception:
                return []
            if multiaxial.epilepsy_cause_known is True:
                if (
                    not multiaxial.epilepsy_cause
                    and not multiaxial.epilepsy_cause_categories
                ):
                    results.append(
                        {
                            "label": "Epilepsy cause",
                            "incomplete": [
                                "Please select at least one epilepsy cause category"
                            ],
                        }
                    )

        return results
