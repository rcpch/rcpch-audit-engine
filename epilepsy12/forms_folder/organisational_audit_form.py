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
            }
        }
