from django import forms
from ..models import OrganisationalAuditSubmission

class OrganisationalAuditSubmissionForm(forms.ModelForm):
    class Meta:
        model = OrganisationalAuditSubmission

        exclude = [
            "submission_period",
            "trust",
            "local_health_board",
            "created_by",
            "updated_by"
        ]

        help_texts = {
            # 1. Workforce

            "S01WTEConsultants": {
                "section": "1. Workforce",
                "question_number": "1.1",
                "label": "How many whole time equivalent general paediatric consultants do you employ?",
                "reference": """
                    <p>
                        Includes general paediatric consultants with 'expertise in epilepsy' (community or hospital based).
                    </p>
                    <p>
                        Audit Unit - The audit unit is defined by your audit unit profile. Most audit units will include one or more secondary tier paediatric services
                        grouped together using pragmatic boundaries agreed by the paediatric audit unit lead, the project team and the tertiary link.
                    </p>
                    <p>
                        WTE = whole time equivalent. E.g One full time post is 1 WTE; Someone working 3 days a week = 0.6 WTE. 2 people both working 3 days a week = 1.2 WTE
                    </p>
                """
            },

            "S01WTEConsultantsEpilepsy": {
                "section": "1. Workforce",
                "question_number": "1.2",
                "label": "Of these, how many have an ‘expertise in epilepsy’?",
                "reference": """
                    <p>
                        Answer using whole time equivalent again. Paediatric neurologists should not be included in your response.
                    </p>
                    <p>
                        Paediatrician with expertise - Paediatric consultant (or associate specialist) defined by themselves, their employer and tertiary service/network as having: training and continuing education in epilepsies AND peer review of practice AND regular audit of diagnosis (e.g. participation in Epilepsy12).
                    </p>
                """
            },

            "S01EpilepsyClinicalLead": {
                "section": "1. Workforce",
                "question_number": "1.3",
                "label": "Do you have a defined paediatric epilepsy clinical lead?"
            },
            "S01EpilepsyClinicalLeadTitle": {
                "parent_question_number": "1.3",
                "label": "Title"
            },
            "S01EpilepsyClinicalLeadFirstName": {
                "parent_question_number": "1.3",
                "label": "First name"
            },
            "S01EpilepsyClinicalLeadSurname": {
                "parent_question_number": "1.3",
                "label": "Surname"
            },

            "S01WTEEpilepsySpecialistNurses": {
                "section": "1. Workforce",
                "question_number": "1.4",
                "label": "How many WTE paediatric epilepsy specialist nurses do you employ?",
                "reference": "Paediatric ESN - A children’s nurse with a defined role and specific qualification and/or training in children’s epilepsies"
            },
            "S01ESNFunctions": {
                "parent_question_number": "1.4",
                "question_number": "1.4i",
                "label": "Which of the following Paediatric ESN functions is the epilepsy service currently able to support?",        
            },

            "S01JobPlannedHoursPerWeekLeadershipQIActivities": {
                "section": "1. Workforce",
                "question_number": "1.5",
                "label": "How many job planned hours are there per week (ESN and/or paediatrician) specified for epilepsy leadership and/or QI activities?",
            },


            # 2. Epilepsy Clinic configuration

            "S02DefinedEpilepsyClinics": {
                "section": "2. Epilepsy Clinic configuration",
                "question_number": "2.1",
                "label": "Does the Health Board/Trust have defined epilepsy clinics seeing patients at a secondary level?",
                "reference": "A secondary level 'epilepsy clinic' is a clinic run just for children with seizures or epilepsy that takes referrals direct from GPs or emergency department (decimal answers are allowed). An ‘Epilepsy Clinic’ is defined as a paediatric clinic where all the children and young people attending have epilepsy or possible epileptic seizures."
            },
            "S02EpilepsyClinicsPerWeek": {
                "parent_question_number": "2.1",
                "question_number": "2.1i",
                "label": "On average, how many consultant (or associate specialist) led secondary level ‘epilepsy clinics’ for children or young people take place within your Health Board/Trust per week?"
            },
            "S02Consultant20Mins": {
                "parent_question_number": "2.1",
                "question_number": "2.1ii",
                "label": "Within the epilepsy clinics, does the clinic booking time allow at least 20 minutes of time with a consultant with expertise in epilepsy and an ESN? (This might be 20 min with the doctor and nurse at the same time or 20 mins each in succession)"
            },

            "S02TFC223": {
                "section": "2. Epilepsy Clinic configuration",
                "question_number": "2.2",
                # TODO MRB: hide this question for Wales
                "label": "Does the Trust currently run TFC 223 Epilepsy Best Practice Criteria (BPC) clinics?",
                "reference": "For Trusts in England only"
            },


            # 3. Tertiary provision

            "S03WTEPaediatricNeurologists": {
                "section": "3. Tertiary provision",
                "question_number": "3.1",
                "label": "How many whole-time equivalent (WTE) paediatric neurologists who manage children with epilepsy do you employ?",
                "reference": """
                    <p>
                        Acutely and or non-acutely.
                    </p>
                    <p>
                        This should not include visiting neurologists who are primarily employed by another trust 
                    </p>
                """
            },

            "S03PathwaysTertiaryPaedNeurology": {
                "section": "3. Tertiary provision",
                "question_number": "3.2",
                "label": "Does you have agreed referral pathways to tertiary paediatric neurology services?"
            },

            "S03PaedNeurologistsDirectReferrals": {
                "section": "3. Tertiary provision",
                "question_number": "3.3",
                "label": "Can paediatric neurologists receive direct referrals from general practice or emergency services to assess children with possible epilepsy?"
            },

            "S03SatellitePaediatricNeurologyClinics": {
                "section": "3. Tertiary provision",
                "question_number": "3.4",
                "label": "Do you host satellite paediatric neurology clinics?",
                "reference": """
                    <p>
                        e.g. a paediatric neurologist visits a site within the trust to undertake paediatric neurology clinics
                    </p>
                    <p>
                        A satellite clinic is where a neurologist supports a clinic outside their base hospital. This might be another hospital or clinic location in their trust or another hospital or clinic location in another trust. 
                    </p>
                """
            },

            # 3.5 itself has no representation in the model, we construct it from the help text alone
            "S03CommenceKetogenicDiet": {
                "section": "3. Tertiary provision",
                "question_number": "3.5i",
                "label": "Commence ketogenic diet",
                "parent_question_number": "3.5",
                "parent_question_label": "Which of the following services can be obtained?",
                "parent_question_reference": "If the child would have to travel to a location outside your audit unit then answer ‘no‘"
            },
            "S03ReviewKetogenicDiet": {
                "question_number": "3.5ii",
                "label": "Ongoing dietetic review of ketogenic diet",
                "parent_question_number": "3.5",
            },
            "S03VNSInsertion": {
                "question_number": "3.5iii",
                "label": "Vagal Nerve Stimulator (VNS) Insertion",
                "parent_question_number": "3.5",
            },
            "S03VNSReview": {
                "question_number": "3.5iv",
                "label": "VNS review",
                "parent_question_number": "3.5"
            },


            # 4. Investigations

            # 4.1 itself has no representation in the model, we construct it from the help text alone
            "S04LeadECG": {
                "section": "4. Investigations",
                "question_number": "4.1i",
                "label": "12 lead ECG",
                "parent_question_number": "4",
                "parent_question_label": "Which of the following investigations can be obtained?",
                "parent_question_reference": "If the child would have to travel to a location outside your audit unit then answer ‘no‘"
            },
            "S04AwakeMRI": {
                "question_number": "4.1ii",
                "label": "'awake' MRI",
                "parent_question_number": "4",
            },
            "S04MriWithSedation": {
                "question_number": "4.1iii",
                "label": "MRI with sedation",
                "parent_question_number": "4",
            },
            "S04MriWithGeneralAnaesthetic": {
                "question_number": "4.1iv",
                "label": "MRI with general anaesthetic",
                "parent_question_number": "4",
            },
            "S04StandardEeg": {
                "question_number": "4.1v",
                "label": "Standard EEG",
                "parent_question_number": "4",
            },
            "S04SleepDeprivedEeg": {
                "question_number": "4.1vi",
                "label": "Sleep deprived EEG",
                "parent_question_number": "4",
            },
            "S04MelatoninInducedEeg": {
                "question_number": "4.1vii",
                "label": "Melatonin induced EEG",
                "parent_question_number": "4",
            },
            "S04SedatedEeg": {
                "question_number": "4.1viii",
                "label": "Sedated EEG",
                "parent_question_number": "4",
            },
            "S042448HAmbulatoryEeg": {
                "question_number": "4.1ix",
                "label": "24/48h ambulatory EEG",
                "parent_question_number": "4",
            },
            "S04InpatientVideoTelemetry": {
                "question_number": "4.1x",
                "label": "Inpatient video telemetry",
                "parent_question_number": "4",
            },
            "S04OutpatientVideoTelemetry": {
                "question_number": "4.1xi",
                "label": "Outpatient video telemetry",
                "parent_question_number": "4",
            },
            "S04HomeVideoTelemetry": {
                "question_number": "4.1xii",
                "label": "Home video telemetry",
                "parent_question_number": "4",
            },
            "S04PortableEEGOnWardAreaWithinTrust": {
                "question_number": "4.1xiii",
                "label": "Portable EEG on ward area within Trust",
                "parent_question_number": "4",
            },
            "S04WholeGenomeSequencing": {
                "question_number": "4.1xiv",
                "label": "Requesting and consenting of Whole Genome Sequencing (WGS)",
                "parent_question_number": "4",
            },


            # 5. Service Contact

            "S05ContactEpilepsyServiceForSpecialistAdvice": {
                "section": "5. Service Contact",
                "question_number": "5.1",
                "label": "Can patients contact the Epilepsy service for specialist advice?",
                "reference": "e.g. from a paediatrician with expertise, paediatric neurologist or ESN) between scheduled reviews?"
            },
            "S05AdviceAvailableAllWeekdays": {
                "question_number": "5.1.1",
                "parent_question_number": "5.1",
                "label": "Is this available all weekdays?"
            },
            "S05AdviceAvailableOutOfHours": {
                "question_number": "5.1.2",
                "parent_question_number": "5.1",
                "label": "Is this available out of hours?"
            },
            "S05AdviceAvailable52WeeksPerYear": {
                "question_number": "5.1.3",
                "parent_question_number": "5.1",
                "label": "Is this available 52 weeks per year?"
            },

            "S05TypicalTimeToAchieveSpecialistAdvice": {
                "section": "5. Service Contact",
                "question_number": "5.2",
                "label": "What would your service describe as a typical time for a parent or young person to achieve specialist advice?"
            },

            "S05WhoProvidesSpecialistAdvice": {
                "section": "5. Service Contact",
                "question_number": "5.3",
                "label": "Who typically provides the initial ‘specialist advice’?"   
            },
            "S05WhoProvidesSpecialistAdviceOther": {
                "parent_question_number": "5.3",
                "parent_question_value": "5",
                "label": "Other"
            },

            "S05evidenceclearpointofcontact": {
                "section": "5. Service Contact",
                "question_number": "5.4",
                "label": "Do you have evidence of a clear point of contact for non‐paediatric professionals seeking paediatric epilepsy support?",
                "reference": "(e.g. school, social care, CAMHS, adult services)"
            },


            # 6. Young People and Transition

            "S06AgreedReferralPathwaysAdultServices": {
                "section": "6. Young People and Transition",
                "question_number": "6.1",
                "label": "Do you have agreed referral pathways to adult services?"
            },

            "S06OutpatientClinicYoungPeopleEpilepsies": {
                "section": "6. Young People and Transition",
                "question_number": "6.2",
                "label": "Do you have a specific outpatient clinic for 'young people' with epilepsies that supports transition?"
            },
            "S06WhatAgeDoesThisClinicAcceptYoungPeople": {
                "question_number": "6.2i",
                "parent_question_number": "6.2",
                "label": "From what age does this clinic typically accept young people?"
            },

            "S06ServiceForEpilepsyBothAdultAndPaed": {
                "section": "6. Young People and Transition",
                "question_number": "6.3",
                "label": "Do you have an outpatient service for epilepsy where there is a presence of both adult and paediatric professionals??"
            },
            "S06IsThisUsually": {
                "question_number": "6.3i",
                "parent_question_number": "6.3",
                "label": "Is this usually:"
            },
            "S06IsThisUsuallyOther": {
                "parent_question_number": "6.3i",
                "parent_question_value": "Oth",
                "label": "Other"
            },
            "S06PercentageOfYoungPeopleTransferred": {
                "question_number": "6.3ii",
                "parent_question_number": "6.3",
                "label": "What percentage of young people transferred to adult services are transitioned through this process?",
                "reference": "Please provide an estimate"
            },

            "S06ProfessionalsRoutinelyInvolvedInTransition": {
                "section": "6. Young People and Transition",
                "question_number": "6.4",
                "label": "Which adult professionals are routinely involved in transition or transfer to adult services?"
            },
            "S06ProfessionalsRoutinelyInvolvedInTransitionOtherDetails": {
                "parent_question_number": "6.4",
                "parent_question_value": "5",
                "label": "Other"
            },

            "S06StructuredResourcesToSupportTransition": {
                "section": "6. Young People and Transition",
                "question_number": "6.5",
                "label": "Do you use structured resources to support transition?",
                "reference": "e.g. Ready Steady Go"
            },


            # 7. Mental health

            "S07ScreenForIssues": {
                "section": "7. Mental health",
                "question_number": "7.1",
                "label": "In the paediatric epilepsy service do you routinely formally screen for mental health disorders?"
            },
            "S07MentalHealthQuestionnaire": {
                "question_number": "7.1i",
                "parent_question_number": "7.1",
                "label": "Which questionnaires do you use?",
            },
            "S07MentalHealthQuestionnaireOtherDetails": {
                "parent_question_number": "7.1i",
                "parent_question_value": "12",
                "label": "Other"
            },

            "S07MentalHealthAgreedPathway": {
                "section": "7. Mental health",
                "question_number": "7.2",
                "label": "Do you have agreed referral pathways for children with any of the following mental health concerns?",
            },
            "S07MentalHealthAgreedPathwayOtherDetails": {
                "parent_question_number": "7.2",
                "parent_question_value": "5",
                "label": "Other"
            },

            "S07MentalHealthProvisionEpilepsyClinics": {
                "section": "7. Mental health",
                "question_number": "7.3",
                "label": "Do you facilitate mental health provision within epilepsy clinics?"
            },
            "S07DoesThisComprise": {
                "question_number": "7.3.1",
                "parent_question_number": "7.3",
                "label": "Does this comprise:"
            },
            "S07DoesThisCompriseOtherSpecify": {
                "parent_question_number": "7.3.1",
                "parent_question_value": "3",
                "label": "Other"
            },
            "S07CurrentTrustActionPlanCoLocatedMentalHealth": {
                "question_number": "7.3.2",
                "parent_question_number": "7.3",
                "parent_question_value": "N",
                "label": "Is there a current action plan describing steps towards co-located mental health provision within epilepsy clinics?",
            },

            "S07TrustAchieve": {
                "section": "7. Mental health",
                "question_number": "7.4",
                "label": "Can you refer to any of the following where required, either within or outside of your audit unit?"
            },


            # 8. Neurodevelopmental support

            "S08ScreenForNeurodevelopmentalConditions": {
                "section": "8. Neurodevelopmental support",
                "question_number": "8.1",
                "label": "Do you routinely formalling screen for neurodevelopmental conditions?"
            },

            "S08AgreedReferralCriteriaChildrenNeurodevelopmental": {
                "section": "8. Neurodevelopmental support",
                "question_number": "8.2",
                "label": "Do you have agreed referral criteria for children with any of the following neurodevelopmental conditions?"
            },
            "S08AgreedReferralCriteriaChildrenNeurodevelopmentalOtherDetails": {
                "label": "Other",
                "parent_question_number": "8.2",
                "parent_question_value": "7"
            },


            # 9. Care Planning

            "S09ComprehensiveCarePlanningChildrenEpilepsy": {
                "section": "9. Care Planning",
                "question_number": "9.1",
                "label": "Do you undertake comprehensive care planning for children with epilepsy?"
            },


            # 10. Patient Database/Register

            "S10TrustMaintainADatabaseOfChildrenWithEpilepsies": {
                "section": "10. Patient Database/Register",
                "question_number": "10.1",
                "label": "Does you maintain a database or register of children with epilepsies?",
                "reference": "Other than the epilepsy12 audit itself"
            }
        }
