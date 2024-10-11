import pandas as pd

from django.forms.fields import TypedChoiceField

from multiselectfield.forms.fields import MultiSelectFormField 

from .models import (
    OrganisationalAuditSubmission,
    Trust,
    LocalHealthBoard
)

from .forms_folder import OrganisationalAuditSubmissionForm

MULTISELECT_FIELD_MAPPINGS = {
    'S01ESNFunctions': {
        "1": 'S01ESNEDVisit',
        "2": 'S01ESNHomeVisit',
        "3": 'S01ESNIndividualHealthcare',
        "4": 'S01ESNNurseLedClinic',
        "5": 'S01ESNNursePrescribing',
        "6": 'S01ESNRescueMedicationParent',
        "7": 'S01ESNRescueMedicationSchool',
        "8": 'S01ESNSchoolMeetings',
        "9": 'S01ESNWardVisits',
        "10": 'S01ESNNoneOfTheAbove'
    },
    'S06ProfessionalsRoutinelyInvolvedInTransition': {
        "1": 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultESN',
        "2": 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultLDESN',
        "3": 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultNeuro',
        "4": 'S06ProfessionalsRoutinelyInvolvedInTransitionYouthWorker',
        "5": 'S06ProfessionalsRoutinelyInvolvedInTransitionOther'
        # The "other" free text field is handled as a normal single value field
    },
    # TODO MRB: should there be an explicit none option?
    'S07MentalHealthQuestionnaire': {
        "1": 'S07MentalHealthQuestionnaireBDI',
        "2": "S07MentalHealthQuestionnaireConnors",
        "3": 'S07MentalHealthQuestionnaireETT',
        "4": 'S07MentalHealthQuestionnaireGAD',
        "5": 'S07MentalHealthQuestionnaireGAD2',
        "6": 'S07MentalHealthQuestionnaireGAD7',
        "7": 'S07MentalHealthQuestionnaireHADS',
        "8": 'S07MentalHealthQuestionnaireMFQ',
        "9": 'S07MentalHealthQuestionnaireNDDI',
        "10": 'S07MentalHealthQuestionnairePHQ',
        "11": 'S07MentalHealthQuestionnaireSDQ',
        "12": 'S07MentalHealthQuestionnaireOther'
    },
    "S07MentalHealthAgreedPathway": {
        "1": 'S07MentalHealthAgreedPathwayAnxiety',
        # 2: 'S07MentalHealthAgreedPathwayDepression' doesn't appear to have a corresponding column in the CSV,
        "3": 'S07MentalHealthAgreedPathwayMoodDisorders',
        "4": 'S07MentalHealthAgreedPathwayNonEpilepticAttackDisorders',
        "5": 'S07MentalHealthAgreedPathwayOtherDetails'
    },
    "S07DoesThisComprise": {
        "1": 'S07DoesThisCompriseEpilepsyClinics',
        "2": 'S07DoesThisCompriseMDT',
        "3": 'S07DoesThisCompriseOther'
    },
    "S07TrustAchieve": {
        "1": 'S07TrustAchieveClinicalPsychology',
        "2": 'S07TrustAchieveEducationalPsychology',
        "3": 'S07TrustAchieveFormalDevelopmental',
        "4": 'S07TrustAchieveNeuropyschology',
        "5": 'S07TrustAchievePsychiatricAssessment',
        "6": 'S07TrustAchieveNone'
    },
    "S08AgreedReferralCriteriaChildrenNeurodevelopmental": {
        "1": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalADHD',
        "2": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalASD',
        "3": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalBehaviour',
        "4": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalDCD',
        "5": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalIntellectualDisability',
        "6": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalLearningDisabilities',
        "7": 'S08AgreedReferralCriteriaChildrenNeurodevelopmentalOtherDetails'
    }
}

def adapt_multiselect_field(row, choices_to_column):
    return [key for key, value in choices_to_column.items() if row[value] == 1]

def import_submissions_from_csv(submission_period, file):
    data = pd.read_csv(file)

    for _, row in data.iterrows():
        ods_code = row["SiteCode"]

        submission = OrganisationalAuditSubmission()
        submission.submission_period = submission_period

        try:
            submission.trust = Trust.objects.get(ods_code=row["SiteCode"])
        except Trust.DoesNotExist:
            submission.local_health_board = LocalHealthBoard.objects.get(ods_code=row["SiteCode"])
        
        field_types = { field.name: type(field.field) for field in OrganisationalAuditSubmissionForm() }

        #######################
        # Single value fields #
        #######################

        for column, raw_value in row.to_dict().items():
            if column in field_types and field_types[column] is not MultiSelectFormField:
                value = None if pd.isnull(raw_value) else raw_value

                # Special case - choice fields need integer values not decimal
                if type(value) == float and field_types[column] == TypedChoiceField:
                    value = int(value)

                # Special case - NA parses as NaN
                if column == "S02TFC223" and pd.isna(raw_value):
                    value = 'NA'

                setattr(submission, column, value)

        ######################
        # Multiselect fields #
        ######################      

        for field, mapping in MULTISELECT_FIELD_MAPPINGS.items():
            values = adapt_multiselect_field(row, mapping)
            setattr(submission, field, values)

        submission.save()

def export_submission_period_as_csv(submission_period):
    columns = ['SiteName', 'SiteCode']
    rows = []

    for field in OrganisationalAuditSubmissionForm():
        if type(field.field) is MultiSelectFormField:
            columns.extend(MULTISELECT_FIELD_MAPPINGS[field.name].values())
        else:
            columns.append(field.name)

    rows = []

    submissions = OrganisationalAuditSubmission.objects.filter(submission_period=submission_period)

    for submission in submissions:
        if submission.local_health_board:
            site_name = submission.local_health_board.name
            site_code = submission.local_health_board.ods_code
        else:
            site_name = submission.trust.name
            site_code = submission.trust.ods_code

        row = {
            'SiteName': site_name,
            'SiteCode': site_code
        }

        for field in OrganisationalAuditSubmissionForm():
            value = getattr(submission, field.name)

            if type(field.field) is MultiSelectFormField:
                selected_choices = list(value)

                for choice, column in MULTISELECT_FIELD_MAPPINGS[field.name].items():
                    row[column] = "1" if choice in selected_choices else "2"
            else:
                row[field.name] = value

        rows.append(row)

    df = pd.DataFrame(data=rows, columns=columns)
    csv = df.to_csv(index=False)

    return csv