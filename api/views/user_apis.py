from .base import UserMixin, APIView
from core.utils import api_response
from api.models.notifications import UserPushNotification
from api.serializers.accounts import ProfileSerializer, UserModel
from api.serializers.rewards import OffersSerializer, Offers


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


class OffersView(UserMixin):
    def get(self, request):
        offer_id = request.GET.get("offer_id")
        if offer_id:
            try:
                offer_obj = Offers.objects.get(offer_id=offer_id)
            except:
                return api_response(False, 404, "Offer does not exits")
            offer_data = OffersSerializer(
                offer_obj,
            ).data
            user_points = request.user.points
            required_points = offer_data.get("required_points", 0)
            user_percentage = int((user_points / required_points) * 100)

            return api_response(
                True,
                200,
                data=offer_data,
                user_points=user_points,
                user_percentage=user_percentage,
            )
        offers = Offers.objects.all()
        serialized_data = OffersSerializer(offers, many=True).data
        eye_health_score = 300
        return api_response(True, 200, data=serialized_data, eye_health_score=eye_health_score)


from api.serializers.prescription import UserPrescriptions, UserPrescriptionsSerializer
from django.http import Http404
from core.utils import api_response

class CustomHttp404(Http404):
    def __init__(self, message=""):
        if not message:
            message = "Custom Not Found Message"
        super().__init__(message)


class UserPrescriptionsView(UserMixin):
    def get_object(self, pk):
        try:
            return UserPrescriptions.objects.get(pk=pk)
        except UserPrescriptions.DoesNotExist:
            raise CustomHttp404()
    
    def get(self, request):
        prescription_id = request.GET.get('prescription_id')
        if prescription_id:
            data = UserPrescriptionsSerializer(self.get_object(prescription_id)).data
            return api_response(True, 200, data=data)

        prescriptions = UserPrescriptions.objects.all()
        serializer = UserPrescriptionsSerializer(prescriptions, many=True)
        return api_response(True, 200, data=serializer.data)

    def post(self, request):
        serializer = UserPrescriptionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return api_response(True, 201, data=serializer.data, message="Prescription uploaded successfully, please wait for admin approval")
        return api_response(False, 400, data=serializer.errors)