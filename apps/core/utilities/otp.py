from __future__ import absolute_import

import datetime
import random

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from pytz import utc
from rest_framework.exceptions import PermissionDenied

from apps.core.models import OneTimePassCode


def create_otp_code():
    """
    Genrates randiom 6 letter string containing numbers and letters
    :return: string: 53F622
    """
    return ''.join(random.choice('0123456789ABCDEF') for i in range(6))


def get_new_otp(user):
    """
    Create a new OTP for user, deletes any existing ones
    :param user: User object
    :return: string: 53F622
    """
    # delete any existing code
    OneTimePassCode.objects.filter(user=user).delete()

    code = create_otp_code()
    expires = datetime.datetime.now(utc) + datetime.timedelta(seconds=settings.OTP_VALIDITY_PERIOD)
    hashed_code = make_password(code)
    OneTimePassCode.objects.create(user=user, code=hashed_code, valid_until=expires)
    return code


def check_valid_otp(user, code_entered):
    """
    Checks if Code entered by the user is Valid or not
    :param user: User object
    :param code_entered: 6 digit code entered by user
    :return: Boolean : True if code valid else raise
    """
    try:
        otp = OneTimePassCode.objects.get(user=user,
                                          valid_until__gt=datetime.datetime.now(utc))
    except OneTimePassCode.DoesNotExist:
        return False
    if not check_password(code_entered, otp.code):
        return False
    return True
