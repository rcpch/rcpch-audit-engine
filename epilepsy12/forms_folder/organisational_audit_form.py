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
                "section": "1. Workforce",
                "parent_question_number": "1.3",
                "label": "Title"
            },
            "S01EpilepsyClinicalLeadFirstName": {
                "section": "1. Workforce",
                "parent_question_number": "1.3",
                "label": "First name"
            },
            "S01EpilepsyClinicalLeadSurname": {
                "section": "1. Workforce",
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
                "section": "1. Workforce",
                "parent_question_number": "1.4",
                "question_number": "1.4i",
                "label": "Which of the following Paediatric ESN functions is the epilepsy service currently able to support?",        
            },
            "S01JobPlannedHoursPerWeekLeadershipQIActivities": {
                "section": "1. Workforce",
                "question_number": "1.5",
                "label": "How many job planned hours are there per week (ESN and/or paediatrician) specified for epilepsy leadership and/or QI activities?",
            },
            "S02DefinedEpilepsyClinics": {
                "section": "2. Epilepsy Clinic configuration",
                "question_number": "2.1",
                "label": "Does the Health Board/Trust have defined epilepsy clinics seeing patients at a secondary level?",
                "reference": "A secondary level 'epilepsy clinic' is a clinic run just for children with seizures or epilepsy that takes referrals direct from GPs or emergency department (decimal answers are allowed). An ‘Epilepsy Clinic’ is defined as a paediatric clinic where all the children and young people attending have epilepsy or possible epileptic seizures."
            },
            "S02EpilepsyClinicsPerWeek": {
                "section": "2. Epilepsy Clinic configuration",
                "parent_question_number": "2.1",
                "question_number": "2.1i",
                "label": "On average, how many consultant (or associate specialist) led secondary level ‘epilepsy clinics’ for children or young people take place within your Health Board/Trust per week?"
            },
            "S02Consultant20Mins": {
                "section": "2. Epilepsy Clinic configuration",
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
            "S03CommenceKetogenicDiet": {
                "section": "3. Tertiary provision",
                "question_number": "3.5i",
                "label": "Commence ketogenic diet",
                "parent_question_number": "3.5",
                "parent_question_label": "Which of the following services can be obtained?",
                "parent_question_reference": "If the child would have to travel to a location outside your audit unit then answer ‘no‘"
            },
            "S03ReviewKetogenicDiet": {
                "section": "3. Tertiary provision",
                "question_number": "3.5ii",
                "label": "Ongoing dietetic review of ketogenic diet",
                "parent_question_number": "3.5",
            },
            "S03VNSInsertion": {
                "section": "3. Tertiary provision",
                "question_number": "3.5iii",
                "label": "Vagal Nerve Stimulator (VNS) Insertion",
                "parent_question_number": "3.5",
            },
            "S03VNSReview": {
                "section": "3. Tertiary provision",
                "question_number": "3.5iv",
                "label": "VNS review",
                "parent_question_number": "3.5"
            },
            "S04LeadECG": {
                "section": "4. Investigations",
                "question_number": "4.1i",
                "label": "12 lead ECG",
                "parent_question_number": "4",
                "parent_question_label": "Which of the following investigations can be obtained?",
                "parent_question_reference": "If the child would have to travel to a location outside your audit unit then answer ‘no‘"
            },
            "S04AwakeMRI": {
                "section": "4. Investigations",
                "question_number": "4.1ii",
                "label": "'awake' MRI",
                "parent_question_number": "4",
            },
            "S04MriWithSedation": {
                "section": "4. Investigations",
                "question_number": "4.1iii",
                "label": "MRI with sedation",
                "parent_question_number": "4",
            },
            "S04MriWithGeneralAnaesthetic": {
                "section": "4. Investigations",
                "question_number": "4.1iv",
                "label": "MRI with general anaesthetic",
                "parent_question_number": "4",
            },
            "S04StandardEeg": {
                "section": "4. Investigations",
                "question_number": "4.1v",
                "label": "Standard EEG",
                "parent_question_number": "4",
            },
            "S04SleepDeprivedEeg": {
                "section": "4. Investigations",
                "question_number": "4.1vi",
                "label": "Sleep deprived EEG",
                "parent_question_number": "4",
            },
            "S04MelatoninInducedEeg": {
                "section": "4. Investigations",
                "question_number": "4.1vii",
                "label": "Melatonin induced EEG",
                "parent_question_number": "4",
            },
            "S04SedatedEeg": {
                "section": "4. Investigations",
                "question_number": "4.1viii",
                "label": "Sedated EEG",
                "parent_question_number": "4",
            },
            "S042448HAmbulatoryEeg": {
                "section": "4. Investigations",
                "question_number": "4.1ix",
                "label": "24/48h ambulatory EEG",
                "parent_question_number": "4",
            },
            "S04InpatientVideoTelemetry": {
                "section": "4. Investigations",
                "question_number": "4.1x",
                "label": "Inpatient video telemetry",
                "parent_question_number": "4",
            },
            "S04OutpatientVideoTelemetry": {
                "section": "4. Investigations",
                "question_number": "4.1xi",
                "label": "Outpatient video telemetry",
                "parent_question_number": "4",
            },
            "S04HomeVideoTelemetry": {
                "section": "4. Investigations",
                "question_number": "4.1xii",
                "label": "Home video telemetry",
                "parent_question_number": "4",
            },
            "S04PortableEEGOnWardAreaWithinTrust": {
                "section": "4. Investigations",
                "question_number": "4.1xiii",
                "label": "Portable EEG on ward area within Trust",
                "parent_question_number": "4",
            },
            "S04WholeGenomeSequencing": {
                "section": "4. Investigations",
                "question_number": "4.1xiv",
                "label": "Requesting and consenting of Whole Genome Sequencing (WGS)",
                "parent_question_number": "4",
            },
        }
