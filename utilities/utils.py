import os
import base64
import pyotp


def get_interval():
    return int(os.getenv("OTP_INTERVAL"))


def otp_object(secret_key):
    secret_key_base32 = base64.b32encode(secret_key.encode()).decode()
    return pyotp.TOTP(secret_key_base32, interval=get_interval())


def generate_otp(username):
    totp = otp_object(username)
    return totp.now()


def verify_otp(username, otp):
    totp = otp_object(username)
    return totp.verify(otp)


import re


def phone_or_email(username):
    if "@" in username:
        return "email"
    else:
        return "phone"


from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)
