# django
from django.contrib.gis.db import models
# 3rd party
from simple_history.models import HistoricalRecords
# rcpch
from ..time_and_user_abstract_base_classes import *


class Organisation(models.Model):
    """
    This class details information about organisations.
    It represents a list of organisations that can be looked up to populate fields in the Site class
    """

    # OrganisationID = models.CharField(
    #     max_length=50,
    #     unique=True,
    #     primary_key=True
    # )
    # OrganisationCode = models.CharField(
    #     max_length=50,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # OrganisationType = models.CharField(
    #     max_length=20,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # SubType = models.CharField(
    #     max_length=50,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Sector = models.CharField(
    #     max_length=20,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # OrganisationStatus = models.CharField(
    #     max_length=50,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # IsPimsManaged = models.CharField(
    #     max_length=20,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # OrganisationName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Address1 = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Address2 = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Address3 = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # City = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # County = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Postcode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Latitude = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Longitude = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # ParentODSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # ParentName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # OPENUKNetworkName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # OPENUKNetworkCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # NHSEnglandRegion = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # NHSEnglandRegionCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # NHSEnglandRegionONSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # ICBName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # ICBODSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # ICBONSBoundaryCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # LocalAuthorityName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # LocalAuthorityODSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # SubICBName = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # SubICBODSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # CountryONSCode = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Country = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Phone = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Email = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Website = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # Fax = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     default=None
    # )
    # DateValid = models.DateTimeField(
    #     blank=True,
    #     null=True,
    #     default=None
    # )
    ODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationTypeId = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationType = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationStatus = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    SummaryText = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    URL = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address1 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address2 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address3 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    City = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    County = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Latitude = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Longitude = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    Postcode = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    Geocode_Coordinates = models.PointField()
    Geocode_CRS = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationSubType = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OrganisationAliases = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ParentOrganisation_ODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ParentOrganisation_OrganisationName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    LastUpdatedDates_ContactDetails = models.DateField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    CCG = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    CCGLocalAuthority = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )

    history = HistoricalRecords()

    # relationships

    nhs_region = models.ForeignKey(
        'epilepsy12.NHSRegionEntity',
        on_delete=models.PROTECT
    )

    integrated_care_board = models.ForeignKey(
        'epilepsy12.IntegratedCareBoardEntity',
        on_delete=models.PROTECT
    )

    country_ons_region = models.ForeignKey(
        'epilepsy12.CountryONSRegionEntity',
        on_delete=models.PROTECT
    )

    openuk_network = models.ForeignKey(
        'epilepsy12.OPENUKNetworkEntity',
        on_delete=models.PROTECT
    )

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        indexes = [models.Index(fields=['OrganisationName'])]
        verbose_name = 'Organisation'
        verbose_name_plural = 'Organisations'
        ordering = ('OrganisationName',)

    def __str__(self) -> str:
        return self.OrganisationName


"""
Organisation Structure from api.nhs.uk

{
            "@search.score": 11.657321,
            "SearchKey": "X99584",
            "ODSCode": "RAL26",
            "OrganisationName": "Barnet Hospital",
            "OrganisationTypeId": "HOS",
            "OrganisationType": "Hospital",
            "OrganisationStatus": "Visible",
            "SummaryText": null,
            "URL": "https://www.royalfree.nhs.uk/",
            "Address1": "Wellhouse Lane",
            "Address2": null,
            "Address3": null,
            "City": "Barnet",
            "County": "Hertfordshire",
            "Latitude": 51.650726318359375,
            "Longitude": -0.21413777768611908,
            "Postcode": "EN5 3DJ",
            "Geocode": {
                "type": "Point",
                "coordinates": [
                    -0.214138,
                    51.6507
                ],
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:4326"
                    }
                }
            },
            "OrganisationSubType": "Independent Sector",
            "OrganisationAliases": [],
            "ParentOrganisation": {
                "ODSCode": "RAL",
                "OrganisationName": "Royal Free London NHS Foundation Trust"
            },
            "Services": [
                {
                    "ServiceName": "Accident and emergency services",
                    "ServiceCode": "SRV0001",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [
                        {
                            "Weekday": "Sunday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Tuesday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Friday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Wednesday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Saturday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Monday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "Thursday",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "General",
                            "AdditionalOpeningDate": "",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "Dec 25 2023",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "Aug 28 2023",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "May 29 2023",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "May  8 2023",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "May  1 2023",
                            "IsOpen": true
                        },
                        {
                            "Weekday": "",
                            "Times": "00:00-23:59",
                            "OpeningTime": "00:00",
                            "ClosingTime": "23:59",
                            "OffsetOpeningTime": 0,
                            "OffsetClosingTime": 1439,
                            "OpeningTimeType": "Additional",
                            "AdditionalOpeningDate": "Dec 26 2023",
                            "IsOpen": true
                        }
                    ],
                    "AgeRange": [
                        {
                            "FromAgeDays": 0,
                            "ToAgeDays": 47481
                        }
                    ],
                    "Metrics": []
                },
                {
                    "ServiceName": "Acute Internal Medicine",
                    "ServiceCode": "SRV0483",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Breast cancer services",
                    "ServiceCode": "SRV0117",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Breast Surgery",
                    "ServiceCode": "SRV0011",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Other symptomatic Breast (2WW)"
                        },
                        {
                            "Name": "Breast cancer family history service"
                        },
                        {
                            "Name": "Oncology Established Diagnosis (non 2WW)"
                        },
                        {
                            "Name": "Mammoplasty (non 2WW)"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Cardiology",
                    "ServiceCode": "SRV0014",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "General Cardiology"
                        },
                        {
                            "Name": "Heart Failure"
                        },
                        {
                            "Name": "Rapid Access Chest Pain inc Exercise ECG"
                        },
                        {
                            "Name": "Lipid Management"
                        },
                        {
                            "Name": "Ischaemic Heart Disease"
                        },
                        {
                            "Name": "Arrhythmia"
                        },
                        {
                            "Name": "Hypertension"
                        },
                        {
                            "Name": "Valve Disorders"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 27 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Children's & Adolescent Services",
                    "ServiceCode": "SRV0017",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Ophthal - Orthoptics"
                        },
                        {
                            "Name": "Ophthal - Strabismus / Ocular Motility"
                        },
                        {
                            "Name": "General ophthalmology - Child and adolescent"
                        },
                        {
                            "Name": "Rheumatology"
                        },
                        {
                            "Name": "Neurology"
                        },
                        {
                            "Name": "Gynaecology"
                        },
                        {
                            "Name": "Immunology"
                        },
                        {
                            "Name": "Diabetes"
                        },
                        {
                            "Name": "General surgery - Child and adolescent"
                        },
                        {
                            "Name": "Cardiology"
                        },
                        {
                            "Name": "Urology"
                        },
                        {
                            "Name": "Oral and Maxillofacial Surgery"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Chronic Obstructive Pulmonary Disease",
                    "ServiceCode": "SRV0548",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Colorectal cancer services",
                    "ServiceCode": "SRV0127",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Dementia Services",
                    "ServiceCode": "SRV0536",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Dermatology",
                    "ServiceCode": "SRV0028",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "General dermatology"
                        },
                        {
                            "Name": "Connective Tissue Disease"
                        },
                        {
                            "Name": "Eczema and Dermatitis"
                        },
                        {
                            "Name": "Patch Testing for Contact Dermatitis"
                        },
                        {
                            "Name": "Vulval Skin Disorders"
                        },
                        {
                            "Name": "Leg Ulcer"
                        },
                        {
                            "Name": "Male Genital Skin Disorders"
                        },
                        {
                            "Name": "Nails"
                        },
                        {
                            "Name": "Hair"
                        },
                        {
                            "Name": "Psoriasis"
                        },
                        {
                            "Name": "Cosmetic Camouflage"
                        },
                        {
                            "Name": "Acne"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 45 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Diabetic Medicine",
                    "ServiceCode": "SRV0029",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Renal Diabetes"
                        },
                        {
                            "Name": "General Diabetic Management"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Diagnostic Physiological Measurement",
                    "ServiceCode": "SRV0327",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Audiology - Hearing Assess / Reassess"
                        },
                        {
                            "Name": "Respiratory - Sleep Apnoea Screening"
                        },
                        {
                            "Name": "Cardiac Physiology - Echocardiogram"
                        },
                        {
                            "Name": "Cardiac Physiology - BP Monitoring"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Ear, Nose & Throat",
                    "ServiceCode": "SRV0032",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Ear"
                        },
                        {
                            "Name": "Throat (incl Voice / Swallowing)"
                        },
                        {
                            "Name": "General ENT treatment"
                        },
                        {
                            "Name": "Salivary Gland"
                        },
                        {
                            "Name": "Hospital hearing tests and aids treatment"
                        },
                        {
                            "Name": "Tinnitus"
                        },
                        {
                            "Name": "Balance / Dizziness"
                        },
                        {
                            "Name": "Nose / Sinus"
                        },
                        {
                            "Name": "Facial Plastic and Skin Lesions"
                        },
                        {
                            "Name": "Neck Lump / Thyroid"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 42 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Emergency Abdominal Surgery",
                    "ServiceCode": "SRV0533",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Endocrinology and Metabolic Medicine",
                    "ServiceCode": "SRV0037",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Pituitary & Hypothalamic"
                        },
                        {
                            "Name": "General endocrinology and metabolic medicine"
                        },
                        {
                            "Name": "Thyroid / Parathyroid"
                        },
                        {
                            "Name": "Gynaecological Endocrinology"
                        },
                        {
                            "Name": "Adrenal Disorders"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Gastrointestinal and Liver services",
                    "ServiceCode": "SRV0042",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Upper GI incl Dyspepsia"
                        },
                        {
                            "Name": "Hepatology"
                        },
                        {
                            "Name": "Colorectal Surgery"
                        },
                        {
                            "Name": "Inflammatory Bowel Disease (IBD)"
                        },
                        {
                            "Name": "Lower GI (medical) excl IBD"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 39 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "General Surgery",
                    "ServiceCode": "SRV0045",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Hernias"
                        },
                        {
                            "Name": "Lumps and Bumps"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 48 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Geriatric Medicine",
                    "ServiceCode": "SRV0048",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "General geriatric medicine"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 36 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Gynaecology",
                    "ServiceCode": "SRV0049",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Infertility"
                        },
                        {
                            "Name": "Menopause"
                        },
                        {
                            "Name": "Menstrual Disorders"
                        },
                        {
                            "Name": "Urogynaecology / Prolapse"
                        },
                        {
                            "Name": "Perineal Repair"
                        },
                        {
                            "Name": "Vulval and Perineal Lesions"
                        },
                        {
                            "Name": "General gynaecology"
                        },
                        {
                            "Name": "Recurrent Miscarriage"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 47 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Haematology",
                    "ServiceCode": "SRV0050",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Clotting Disorders"
                        },
                        {
                            "Name": "General haematology"
                        },
                        {
                            "Name": "Anti Coagulant"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Inpatient Diabetes",
                    "ServiceCode": "SRV0547",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Intensive Care",
                    "ServiceCode": "SRV0534",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Major trauma",
                    "ServiceCode": "SRV0493",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Maternity services",
                    "ServiceCode": "SRV0370",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Neonatal Care",
                    "ServiceCode": "SRV0537",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Nephrology",
                    "ServiceCode": "SRV0091",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Renal Diabetes"
                        },
                        {
                            "Name": "Hypertension"
                        },
                        {
                            "Name": "Nephrology"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Neurology",
                    "ServiceCode": "SRV0064",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Parkinsons / Movement Disorders"
                        },
                        {
                            "Name": "General neurology"
                        },
                        {
                            "Name": "Epilepsy"
                        },
                        {
                            "Name": "Headache and migraine"
                        },
                        {
                            "Name": "Cognitive Disorders"
                        },
                        {
                            "Name": "Neuromuscular"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 36 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Obstetrics And Gynaecology",
                    "ServiceCode": "SRV0485",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Ophthalmology",
                    "ServiceCode": "SRV0070",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Glaucoma"
                        },
                        {
                            "Name": "Low Vision"
                        },
                        {
                            "Name": "Cataract"
                        },
                        {
                            "Name": "Oculoplastics/Orbits/Lacrimal"
                        },
                        {
                            "Name": "Orthoptics"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 36 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Oral and Maxillofacial Surgery",
                    "ServiceCode": "SRV0071",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Oncology (Established Diagnosis)"
                        },
                        {
                            "Name": "Salivary Gland Disease"
                        },
                        {
                            "Name": "Head and Neck Lumps (not 2WW)"
                        },
                        {
                            "Name": "Facial Plastics"
                        },
                        {
                            "Name": "Oral Surgery"
                        },
                        {
                            "Name": "Facial Deformity"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Numbers of patients too low to report a waiting time ",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "NULL"
                        }
                    ]
                },
                {
                    "ServiceName": "Orthopaedics",
                    "ServiceCode": "SRV0073",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Foot and Ankle"
                        },
                        {
                            "Name": "Knee replacement"
                        },
                        {
                            "Name": "Hip Fracture"
                        },
                        {
                            "Name": "Hip replacement"
                        },
                        {
                            "Name": "Hand and Wrist"
                        },
                        {
                            "Name": "Fracture - Non Emergency"
                        },
                        {
                            "Name": "Sports Trauma"
                        },
                        {
                            "Name": "Spine - Neck Pain"
                        },
                        {
                            "Name": "Spine - Back Pain (not Scoliosis/Deform)"
                        },
                        {
                            "Name": "Podiatric Surgery"
                        },
                        {
                            "Name": "Shoulder and Elbow"
                        },
                        {
                            "Name": "Spine - Scoliosis and Deformity"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 58 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Paediatric Surgery",
                    "ServiceCode": "SRV0544",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Pain Management",
                    "ServiceCode": "SRV0076",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Pain Management"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Physiotherapy",
                    "ServiceCode": "SRV0081",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Musculoskeletal"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Plastic surgery",
                    "ServiceCode": "SRV0082",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Minor Plastic Surgery"
                        },
                        {
                            "Name": "Mammoplasty"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 54 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Podiatry",
                    "ServiceCode": "SRV0083",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Nail Surgery"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Prostate Cancer Service",
                    "ServiceCode": "SRV0538",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Respiratory Medicine",
                    "ServiceCode": "SRV0092",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "General respiratory medicine"
                        },
                        {
                            "Name": "Occupational Lung Disease"
                        },
                        {
                            "Name": "Asthma"
                        },
                        {
                            "Name": "Interstitial Lung Disease"
                        },
                        {
                            "Name": "COPD"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 41 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Rheumatology",
                    "ServiceCode": "SRV0093",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Bone / Osteoporosis"
                        },
                        {
                            "Name": "Musculoskeletal"
                        },
                        {
                            "Name": "Inflammatory Arthritis"
                        },
                        {
                            "Name": "Other Autoimmune Rheumatic Disease"
                        },
                        {
                            "Name": "Spinal Disorders"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 32 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Stroke",
                    "ServiceCode": "SRV0174",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                },
                {
                    "ServiceName": "Urology",
                    "ServiceCode": "SRV0103",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": [
                        {
                            "MetricID": 74,
                            "MetricName": "RTT 92%",
                            "Description": "Weeks within which 92% of patients were treated",
                            "Text": "Up to 49 weeks for 9/10 patients",
                            "LinkText": null,
                            "MetricDisplayTypeID": 5,
                            "BandingClassification": "Exclamation"
                        }
                    ]
                },
                {
                    "ServiceName": "Vascular surgery",
                    "ServiceCode": "SRV0104",
                    "ServiceDescription": null,
                    "Contacts": [],
                    "ServiceProvider": {
                        "ODSCode": "RAL",
                        "OrganisationName": "Royal Free London NHS Foundation Trust"
                    },
                    "Treatments": [
                        {
                            "Name": "Varicose Veins"
                        },
                        {
                            "Name": "Arterial"
                        },
                        {
                            "Name": "Leg Ulcer"
                        },
                        {
                            "Name": "General vascular surgery"
                        }
                    ],
                    "OpeningTimes": [],
                    "AgeRange": [],
                    "Metrics": []
                }
            ],
            "OpeningTimes": [],
            "Contacts": [
                {
                    "ContactType": "PALS",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Email",
                    "ContactValue": "bcfpals@nhs.net"
                },
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Telephone",
                    "ContactValue": "020 8216 4600"
                },
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Website",
                    "ContactValue": "https://www.royalfree.nhs.uk/"
                }
            ],
            "Facilities": [],
            "Staff": [],
            "GSD": null,
            "LastUpdatedDates": {
                "OpeningTimes": null,
                "BankHolidayOpeningTimes": null,
                "DentistsAcceptingPatients": null,
                "Facilities": "2014-02-26T13:06:12Z",
                "HospitalDepartment": "2023-04-20T01:37:52.803Z",
                "Services": "2014-02-26T13:06:12Z",
                "ContactDetails": "2019-11-26T10:23:16Z",
                "AcceptingPatients": null
            },
            "AcceptingPatients": {
                "GP": null,
                "Dentist": []
            },
            "GPRegistration": null,
            "CCG": null,
            "RelatedIAPTCCGs": [],
            "CCGLocalAuthority": [],
            "Trusts": [],
            "Metrics": [
                {
                    "MetricID": 8175,
                    "MetricName": "Care Quality Commission inspection ratings shadowed",
                    "DisplayName": "Care Quality Commission inspection ratings",
                    "Description": "Care Quality Commission inspection ratings",
                    "Value": "3",
                    "Value2": null,
                    "Value3": null,
                    "Text": "Requires Improvement",
                    "LinkUrl": "http://www.cqc.org.uk/location/RAL26",
                    "LinkText": "Visit CQC profile",
                    "MetricDisplayTypeID": 5,
                    "MetricDisplayTypeName": "BandingImage",
                    "HospitalSectorType": "Independent Sector",
                    "MetricText": "[BandingName]",
                    "DefaultText": null,
                    "IsMetaMetric": true,
                    "BandingClassification": "cqc-requiresimp",
                    "BandingName": "Requires Improvement"
                }
            ]
        }
"""
