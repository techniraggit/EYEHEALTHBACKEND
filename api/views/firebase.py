import os
import requests
from api.models.notifications import PushNotification, UserPushNotification
from api.models.accounts import UserModel
from core.logs import Logger

logger = Logger("notifications.logs")

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")


# def send_push_notification(device_token, title, message):
#     url = "https://fcm.googleapis.com/fcm/send"
#     headers = {"Authorization": f"Key={FCM_SERVER_KEY}"}
#     data = {
#         "to": device_token,
#         "notification": {
#             "title": title,
#             "body": message,
#         },
#     }
#     response = requests.post(url, json=data, headers=headers)
#     return response


def send_firebase_notification(device_tokens: list, title: str, message: str):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {"Authorization": f"Key={FCM_SERVER_KEY}"}
    data = {
        "registration_ids": device_tokens,
        "notification": {
            "title": title,
            "body": message,
        },
    }
    response = requests.post(url, json=data, headers=headers)
    return response


def create_notification(user_ids: list, title: str, message: str):
    try:
        user_objs = UserModel.objects.filter(id__in=user_ids).prefetch_related(
            "device_info"
        )
        push_notification_obj = PushNotification.objects.create(
            title=title, message=message
        )
        notification_objs = []
        for user_obj in user_objs:
            notification_objs.append(
                UserPushNotification(user=user_obj, notification=push_notification_obj)
            )
        UserPushNotification.objects.bulk_create(notification_objs)
        device_tokens = [
            device.token for user in user_objs for device in user.device_info.all()
        ]
        send_firebase_notification(device_tokens, title, message)
        return True
    except Exception as e:
        logger.error(str(e))
        return False
