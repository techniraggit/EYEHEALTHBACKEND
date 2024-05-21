from rest_framework_simplejwt.tokens import RefreshToken
import os
import base64
import pyotp


def get_interval():
    return int(os.getenv("OTP_INTERVAL"))


def get_otp_digits():
    return int(os.getenv("OTP_DIGITS"))


def otp_object(secret_key):
    secret_key_base32 = base64.b32encode(secret_key.encode()).decode()
    return pyotp.TOTP(
        secret_key_base32, interval=get_interval(), digits=get_otp_digits()
    )


def generate_otp(username):
    totp = otp_object(username)
    return totp.now()


def verify_otp(username, otp):
    totp = otp_object(username)
    return totp.verify(otp)


def phone_or_email(username):
    if "@" in username:
        return "email"
    else:
        return "phone"


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)
