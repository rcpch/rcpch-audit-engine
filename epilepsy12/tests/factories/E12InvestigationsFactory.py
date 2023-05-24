"""Factory fn to create new E12 Investigations, related to a created Registration.
"""
# standard imports
from dateutil.relativedelta import relativedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Investigations
)

class E12InvestigationsFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Investigations.
    
    This Factory is generated AFTER a Registration is created.
    
    Default:
        - EEG requested on registration plus 1 month
        - EEG performed on request date + 28 days
        - MRI requested on registration plus 1 month
        - MRI reported on request date + 28 days
        - ECG + CTHead performed
    Flags:
        - `eeg_not_requested` : if True, sets request to False + dates to None
        - `mri_not_requested` : if True, sets request to False + dates to None
    """
    class Meta:
        model = Investigations
    
    # Once Registration instance made, it will attach to this instance
    registration = None
    
    eeg_indicated = True
    # eeg requested is 365 days before registration
    @factory.lazy_attribute
    def eeg_request_date(self): 
        return self.registration.registration_date + relativedelta(months=1)
    # eeg performed is 28 days after requested date
    @factory.lazy_attribute
    def eeg_performed_date(self): 
        return self.eeg_request_date + relativedelta(days=28)
    
    mri_indicated = True
    # mri requested is 365 days before registration
    @factory.lazy_attribute
    def mri_brain_requested_date(self): 
        return self.registration.registration_date + relativedelta(months=1)
    # mri reported is 28 days after requested date
    @factory.lazy_attribute
    def mri_brain_reported_date(self): 
        return self.mri_brain_requested_date + relativedelta(days=28)
    
    twelve_lead_ecg_status = True
    ct_head_scan_status = True
    
    class Params:
        eeg_not_requested = factory.Trait(
            eeg_indicated = False,
            eeg_request_date = None,
            eeg_performed_date = None,
        )
        mri_not_requested = factory.Trait(
            mri_indicated = False,
            mri_brain_requested_date = None,
            mri_brain_reported_date = None,
        )