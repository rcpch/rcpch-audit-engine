# import constants
from .constants import *

# import tables
from .models import *

"""
Stated Aims of the Audit
• Continue to measure and improve care and outcomes for children and young people with
epilepsies
• Include all children and young people with a new onset of epilepsy,
• Enable continuous patient ascertainment,
• Use a pragmatic and concise dataset,
• Incorporate NICE Quality Standards alongside metrics about mental health, education and
transition to adult services,
• Provide services with local real-time patient- and service-level reporting.

Quality Improvement
- Supporting regional and national quality improvement activities
- Epilepsy Quality Improvement Programme (EQIP)
- Involving children and young people

There are 12 key performance indicators:
1. Input into care from a paediatrician with expertise in epilepsies,
2. Input into care from an epilepsy specialist nurse (ESNs),
3. (a) Appropriate tertiary input into care, and (b) appropriate epilepsy surgery referral
4. Appropriate first paediatric assessment,
5. Recorded seizure formulation,
6. Access to electrocardiogram (ECG),
7. Access to magnetic resonance imaging (MRI),
8. Accuracy of diagnosis,
9. (a) Discussion of the risks where sodium valproate is used in treatment for girls aged 9 and over,
and (b) girls and young women prescribed sodium valproate
10. Comprehensive care plan that is updated and agreed with the patient,
11. Documented evidence of all key elements of care planning content,
12. Record of a school individual healthcare plan.

Schema
------
*Main classes - these are all found in the epilepsy12/models folder*

The Case class records information about each young person
The Registration class holds a record for each audit.
The Assessment class holds information on cases gathered over the one year audit period.
The InitialAssessment class is closely linked to Assessment and holds the minimum expected information collected at first assessment.  
The Investigations class records dates that initial tests were recorded (ECG, EEG, CT and MRI)
The EpilepsyContext class records contextual information that defines epilepsy risk.
The Comorbidity class records information on emotional, behavioural, neurodevelopmental and neuropsychatric comorbidities

The RescueMedicine class records information on rescue medicines used.
The AntiEpilepsyDrug class records information about antiepilepsy drugs.

The SeizureType class describes the seizure type.
The ElectroClinicalSydrome class records information on electroclinical syndromes.
The SeizureCause class records the cause of each seizure.
The NonEpilepsy class records information about nonepilepsy features of episode.

The Site class records information about each site that oversees the epilepsy care of each case.
The HospitalTrust class records hospital trust details. It is used as a look up class for the Site class.


Relationships
-------------
Case to Registration 1:1
Case to Site 1:n
Case to Comorbidity n:n

Registration to Assessment 1:1
InitialAssessment to Assessment 1:1
InitialAssessment to EpilepsyContext  1:1

Comorbidity to Case n:n

Assessment to Investigations n:n
Assessment to RescueMedicine 1:n
Assessment to ElectroClinicalSyndrome 1:1
Assessment to SeizureCause n:n
Assessment to SeizureType 1:n
Assessment to AntiEpilepsyDrug n:n
Assessment to RescueMedicine n:n
Assessment to NonEpilepsy 1:1

HospitalTrust to Site 1:n

"""



"""
COMMENTING OUT THESE TABLES AND REPLACING WITH COMORBIDITIES
"""

# class MentalHealth(base.Model): 
#     """
#     This class records information about a given mental health condition
#     It references the Case class, as each child might have several mental health conditions
#     """
#     mental_health_problem=models.CharField( # TODO #8 Decision to leave mental health problems the same: will need to be SNOMED in future
#         max_length=3,
#         choices=NEUROPSYCHIATRIC
#     )
#     mental_health_problem_snomed_code=models.CharField(
#         max_length=50
#     ) # this is a new field - decision not to act on this currently: rare for a formal diagnosis to be give so
#     # not practical
#     emotional_problem=models.CharField(
#         max_length=3, 
#         choices=DEVELOPMENTAL_BEHAVIOURAL
#     )
#     emotional_problem_snomed_code=models.CharField(max_length=50) # this is a new field
#     case = models.ForeignKey(
#         Case,
#         on_delete=CASCADE,
#         primary_key=True
#     )

# class Neurodevelopment(base.Model):
#     """
#     This class records information about a given neurodevelopmental condition
#     It references the Case class, as each child might have several neurodevelopmental conditions
#     """
#     neurodevelopmental_problem=models.CharField(
#         max_length=3, 
#         choices=NEURODEVELOPMENTAL
#     )
#     neurodevelopmental_problem_other=models.CharField(max_length=250)
#     neurodevelopmental_problem_snomed_code=models.CharField(max_length=50) # this is a new field
#     neurodevelopmental_problem_severity=models.CharField(
#         max_length=3,
#         choices=DISORDER_SEVERITY
#     )
#     case = models.ForeignKey(
#         Case,
#         on_delete=CASCADE,
#         primary_key=True
#     )