import requests
from django.conf import settings
from core.logs import Logger

logger = Logger("sms.logs")


def send_sms(phone, message):
    payload = {
        "userid": settings.CBIS_SMS_USERNAME,
        "password": settings.CBIS_SMS_PASSWORD,
        "sendMethod": "quick",
        "mobile": phone,
        "msg": message,
        "senderid": settings.CBIS_SMS_SENDER_ID,
        "msgType": "text",
        "duplicatecheck": "true",
        "output": "json",
    }
    headers = {
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
    }

    response = requests.post(settings.CBIS_SMS_BASEURL, data=payload, headers=headers)

    if response.status_code != 200:
        logger.error(response.status_code)
        return False
    else:
        return True
