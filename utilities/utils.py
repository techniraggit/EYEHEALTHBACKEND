import re
import json
import pytz
from datetime import datetime
import random
import string
from django.template.loader import get_template
from weasyprint import HTML, CSS
from rest_framework_simplejwt.tokens import RefreshToken
import os
import base64
import pyotp

STATIC_LOGINS = json.loads(os.environ.get("STATIC_LOGINS", "[]"))

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
    username = str(username).replace("+91", "")
    if username in STATIC_LOGINS:
        return "1234"
    totp = otp_object(username)
    return totp.now()


def verify_otp(username, otp):
    username = str(username).replace("+91", "")
    if username in STATIC_LOGINS:
        return True
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
        data_bytes = data.encode("utf-8")
    elif isinstance(data, int):
        data_bytes = str(data).encode("utf-8")
    else:
        raise TypeError("Data must be a string or an integer")

    return str(base64.b64encode(data_bytes)).split("'")[1]


def base64_decode(encoded_data: bytes) -> str:
    decoded_bytes = base64.b64decode(encoded_data)
    return decoded_bytes.decode("utf-8")


def generate_pdf(template_name, context_data, page_width="9.5in", page_height="11.6in"):
    template = get_template(template_name)
    html_content = template.render(context_data)
    html = HTML(string=html_content)
    html = html.render(
        stylesheets=[CSS(string=f"@page {{ size: {page_width} {page_height}; }}")]
    )
    pdf_file = html.write_pdf()
    return pdf_file


def time_localize(datetime_object: datetime):
    timezone = pytz.timezone("Asia/Kolkata")
    return datetime_object.astimezone(timezone)


def dlt_value():
    from uuid import uuid4

    return f"/{str(uuid4()).split('-')[0]}"


def get_form_error_msg(form_errors: json):
    errors = form_errors
    parsed_data = json.loads(errors)
    first_key = next(iter(parsed_data))
    first_object = parsed_data[first_key][0]
    message = f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
    return message


def is_valid_phone(phone_number):
    """ "+1" and "+91" prefixes validate before a 10-digit number."""
    pattern = re.compile(r"^\+(1|91)\d{10}$")
    if phone_number:
        if re.match(pattern, phone_number):
            return True
    return False


def is_valid_email(email):
    EMAIL_REGEX = re.compile(
        r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|'
        r'(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|'
        r"(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
    )
    return True if EMAIL_REGEX.match(email) else False


def generate_password(length=5):
    characters = string.ascii_letters + string.digits
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def get_object_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except:
        return None