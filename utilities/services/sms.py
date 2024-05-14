import os
from twilio.rest import Client

# account_sid = os.environ['TWILIO_ACCOUNT_SID']
# auth_token = os.environ['TWILIO_AUTH_TOKEN']
# phone_number = os.environ['TWILIO_NUMBER']
# client = Client(account_sid, auth_token)


def send_sms(mobile, message):
    # client = Client(account_sid, auth_token)
    try:
        # message = client.messages.create(
        #     body=f"{message}", from_=phone_number, to=f"+91{mobile}"
        # )
        return True
    except Exception as e:
        return False
