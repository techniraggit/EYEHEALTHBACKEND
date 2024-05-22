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


def base64_encode(data):
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, int):
        data_bytes = str(data).encode('utf-8')
    else:
        raise TypeError("Data must be a string or an integer")

    return str(base64.b64encode(data_bytes)).split("'")[1]


def base64_decode(encoded_data: bytes) -> str:
    decoded_bytes = base64.b64decode(encoded_data)
    return decoded_bytes.decode("utf-8")
