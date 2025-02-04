from api.models.notifications import (
    PushNotification,
    UserPushNotification,
    UserModel,
)
import os
import pathlib
from core.logs import Logger
import firebase_admin
from firebase_admin import (
    credentials,
    messaging,
)

logger = Logger("notification.log")


def get_certificate_file_path(file_name="firebase_admin_sdk.json"):
    return os.path.join(pathlib.Path(__file__).parent.parent.parent, file_name)

def send_(title:str, body:str, token:str):
    if not firebase_admin._apps:
        cred = credentials.Certificate(get_certificate_file_path())
        firebase_admin.initialize_app(cred)

    # Android notification configuration
    android_config = messaging.AndroidConfig(
        notification=messaging.AndroidNotification(
            title=title,
            body=body,
            sound="default",
            click_action="FLUTTER_NOTIFICATION_CLICK",
        )
    )

    # iOS notification configuration
    ios_config = messaging.APNSConfig(
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(title=title, body=body),
                sound="default",
            )
        )
    )

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        android=android_config,
        apns=ios_config,
    )

    try:
        messaging.send(message)
    except Exception as e:
        print("Error sending message:", e)


def send_firebase_notification(device_tokens: list, title: str, message: str):
    for token in device_tokens:
        send_(
            title=title,
            body=message,
            token=token
        )


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
