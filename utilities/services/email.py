from django.core.mail import (
    EmailMultiAlternatives,
)
from django.conf import settings


def send_email(
    subject: str,
    message: str,
    recipients: list,
    cc:list=None,
    attachment=None,
    file_type=None,
    file_name=None,
):
    try:
        email = EmailMultiAlternatives(
            subject, message, settings.DEFAULT_FROM_EMAIL, recipients, cc=cc
        )

        if attachment:
            email.attach(file_name, attachment, file_type)
            email.attach_alternative(message, "text/html")
        else:
            email.attach_alternative(message, "text/html")

        email.send()
        return True
    except Exception as e:
        # raise e
        return False
