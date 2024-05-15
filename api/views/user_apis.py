from .base import UserMixin
from core.utils import api_response
from api.models.notifications import UserPushNotification
from api.serializers.accounts import ProfileSerializer, UserModel


class ProfileView(UserMixin):
    def get(self, request):
        user = ProfileSerializer(request.user).data
        return api_response(True, 200, data=user)

    def patch(self, request):
        try:
            user_obj = UserModel.objects.get(id=request.data.get("id"))
        except:
            return api_response(False, 404, "User does not exist")

        serializer = ProfileSerializer(user_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                True, 200, "Profile updated successfully.", data=serializer.data
            )
        return api_response(False, 400, serializer.errors)


class NotificationView(UserMixin):
    def get(self, request):
        notifications = (
            UserPushNotification.objects.filter(user=request.user)
            .select_related("notification")
            .order_by("-created_on")
        )
        push_notification = []
        is_read_false_count = notifications.filter(is_read=False).count()
        for notification in notifications:
            push_notification.append(
                {
                    "id": notification.id,
                    "title": notification.notification.title,
                    "message": notification.notification.message,
                    "created": notification.notification.created_on,
                    "is_read": notification.is_read,
                }
            )
        return api_response(
            True, 200, data=push_notification, is_read_false_count=is_read_false_count
        )

    def put(self, request):
        id = request.data.get("id")
        if not id:
            return api_response(False, 400, "Id required")

        try:
            user_notification = UserPushNotification.objects.get(id=id)
        except:
            return api_response(False, 404, "Notification not found")
        user_notification.is_read = True
        user_notification.save()
        data = [
            {
                "id": user_notification.id,
                "title": user_notification.notification.title,
                "message": user_notification.notification.message,
                "created": user_notification.notification.created_on,
                "is_read": user_notification.is_read,
            }
        ]
        return api_response(True, 200, data=data)
