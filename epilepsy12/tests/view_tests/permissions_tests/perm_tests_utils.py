from django_otp import DEVICE_ID_SESSION_KEY
from django_otp import devices_for_user
from two_factor.utils import default_device

def twofactor_signin(client, test_user)->None:
    """Helper fn to verify user via 2fa"""
    # OTP ENABLE
    test_user.totpdevice_set.create(name='default')
    session = client.session
    session[DEVICE_ID_SESSION_KEY] = default_device(test_user).persistent_id
    session.save()