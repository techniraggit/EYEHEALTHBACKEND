from api.models.notifications import PushNotification, UserPushNotification, UserModel
import requests
import os
from core.logs import Logger

logger = Logger("notification.log")

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")


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
