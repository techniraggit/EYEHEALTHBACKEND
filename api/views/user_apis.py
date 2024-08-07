from utilities.utils import dlt_value
from django.db.models import Q
from api.models.accounts import OTPLog
from api.models.rewards import GlobalPointsModel
from django.db.models.functions import Concat
from django.db.models import F, Value, Sum
from core.utils import api_response, custom_404
from api.serializers.prescription import UserPrescriptions, UserPrescriptionsSerializer
from .base import UserMixin, ERROR_500_MSG
from api.models.notifications import UserPushNotification
from api.serializers.accounts import (
    ProfileSerializer,
    UserModel,
    UserAddressSerializer,
    UserAddress,
    ReferTrack,
)
from api.serializers.rewards import (
    OffersSerializer,
    Offers,
    UserRedeemedOffersSerializer,
)
from api.models.rewards import UserRedeemedOffers
from api.models.accounts import UserPoints
from api.models.eye_health import EyeFatigueReport, EyeTestReport
from api.models.dashboard import CarouselModel
from api.serializers.dashboard import CarouselModelSerializer
import logging

logger = logging.getLogger(__name__)


class Dashboard(UserMixin):
    def get(self, request):
        request_user_id = request.user.id
        eye_test_count = EyeTestReport.objects.filter(user_profile__user__id=request_user_id).count()
        eye_fatigue_count = EyeFatigueReport.objects.filter(user=request.user).count()
        eye_health_score = EyeTestReport.objects.filter(
            user_profile__user__id=request_user_id,
            user_profile__full_name=request.user.get_full_name(),
            # user_profile__age=request.user.age(),
        )
        prescription_obj = UserPrescriptions.objects.filter(user=request.user)

        # Carousel data
        carousel_data = CarouselModelSerializer(
            CarouselModel.objects.filter(is_active=True),
            many=True,
            fields=["name", "image"],
            context={'request': request}
        ).data
        return api_response(
            True,
            200,
            total_eye_test_count=eye_test_count,
            total_eye_fatigue_count=eye_fatigue_count,
            eye_health_score=(
                eye_health_score.first().health_score if eye_health_score.first() else 0
            ),
            is_prescription_uploaded=prescription_obj.exists(),
            visits_to_optometry=prescription_obj.filter(status="approved").count(),
            carousel=carousel_data,
        )


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

    def patch(self, request):
        UserPushNotification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        return api_response(True, 200, "All notifications marked as read")


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
            user_percentage = (
                min(100, int((user_points / required_points) * 100))
                if required_points > 0
                else 100
            )

            return api_response(
                True,
                200,
                data=offer_data,
                user_points=user_points,
                user_percentage=user_percentage,
            )

        offers = Offers.objects.all()
        serialized_data = OffersSerializer(offers, many=True).data

        eye_health_score = EyeTestReport.objects.filter(
            user_profile__user=request.user,
            user_profile__full_name=request.user.get_full_name(),
            health_score__gt=0,
        ).order_by("-created_on")

        eye_health_score = (
            eye_health_score.first().health_score if eye_health_score.first() else 0
        )

        return api_response(
            True, 200, data=serialized_data, eye_health_score=eye_health_score
        )


class UserPrescriptionsView(UserMixin):
    def get_object(self, pk):
        try:
            return UserPrescriptions.objects.get(pk=pk)
        except UserPrescriptions.DoesNotExist:
            raise custom_404("The prescription does not exist.")

    def get(self, request):
        prescription_id = request.GET.get("prescription_id")
        if prescription_id:
            data = UserPrescriptionsSerializer(self.get_object(prescription_id)).data
            return api_response(True, 200, data=data)

        total_points = UserPoints.objects.filter(
            user=request.user, event_type="prescription_upload"
        ).aggregate(total=Sum("points"))["total"]

        total_points = total_points or 0  # Handle case where total_points is None
        prescription_upload_points = GlobalPointsModel.objects.get(
            event_type="prescription_upload"
        ).value

        prescriptions = UserPrescriptions.objects.filter(user=request.user)
        serializer = UserPrescriptionsSerializer(prescriptions, many=True)
        return api_response(
            True,
            200,
            data=serializer.data,
            total_points_by_prescription_upload=total_points,
            you_can_get_points_by_prescription_upload=prescription_upload_points,
        )

    def post(self, request):
        serializer = UserPrescriptionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return api_response(
                True,
                201,
                data=serializer.data,
                message="Prescription uploaded successfully, please wait for admin approval",
            )
        return api_response(False, 400, data=serializer.errors)


class UserAddressesView(UserMixin):
    def get(self, request):
        address_id =  request.GET.get('address_id')
        if address_id:
            user_address = UserAddress.objects.filter(user=request.user, address_id=address_id)
            serializer = UserAddressSerializer(user_address, many=True)
            return api_response(True, 200, data=serializer.data)

        user_address = UserAddress.objects.filter(user=request.user)
        serializer = UserAddressSerializer(user_address, many=True)
        return api_response(True, 200, data=serializer.data)

    def post(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return api_response(
                True, 201, data=serializer.data, message="Address added successfully"
            )
        return api_response(False, 400, data=serializer.errors)

    def patch(self, request):
        address_id = request.data.get("address_id")

        if not address_id:
            return api_response(False, 400, "address_id required")

        try:
            user_address = UserAddress.objects.get(address_id=address_id)
        except UserAddress.DoesNotExist:
            return api_response(False, 404, "UserAddress not found")

        serializer = UserAddressSerializer(
            user_address, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return api_response(
                True, 200, "Address updated successfully", data=serializer.data
            )
        return api_response(False, 400, message=serializer.errors)

    def delete(self, request):
        address_id = request.GET.get("address_id")
        if not address_id:
            return api_response(False, 400, "address_id required")

        try:
            user_address = UserAddress.objects.get(address_id=address_id)
        except UserAddress.DoesNotExist:
            return api_response(False, 404, "UserAddress not found")

        user_address.delete()
        return api_response(True, 200, message="Address deleted successfully")


class MyReferralsView(UserMixin):
    def get(self, request):
        refer_objs = (
            ReferTrack.objects.filter(referred_by=request.user)
            .select_related("user")
            .annotate(
                full_name=Concat(
                    F("user__first_name"), Value(" "), F("user__last_name")
                ),
                phone=F("user__phone_number"),
            )
            .values("full_name", "phone")
        )

        data = list(refer_objs)
        return api_response(True, 200, data=data)


class UserRedeemedOffersView(UserMixin):
    def get(self, request):
        fields = ["id", "offer", "status", "redeemed_on", "address"]
        id = request.GET.get("id")
        if id:
            try:
                queryset = UserRedeemedOffers.objects.get(id=id)
            except:
                return api_response(False, 404, "Offer not found")
            serialized_data = UserRedeemedOffersSerializer(queryset, fields=fields).data
            return api_response(True, 200, data=serialized_data)
        queryset = UserRedeemedOffers.objects.filter(user=request.user)
        serialized_data = UserRedeemedOffersSerializer(
            queryset, many=True, fields=fields
        ).data
        return api_response(True, 200, data=serialized_data)

    def post(self, request):
        offer_id = request.data.get("offer_id")
        address_id = request.data.get("address_id")
        if not offer_id:
            return api_response(False, 400, "Offer id required")
        try:
            offer_obj = Offers.objects.get(offer_id=offer_id)
        except:
            return api_response(False, 404, "Offer does not exits")

        user_obj = UserModel.objects.get(pk=request.user.pk)

        offer_required_points = int(offer_obj.required_points)
        if user_obj.points < offer_required_points:
            return api_response(False, 400, "You don't have enough points")

        address_obj = None
        if address_id:
            try:
                address_obj = UserAddress.objects.get(address_id=address_id)
            except:
                return api_response(False, 404, "Address does not exits")

        data = {
            "user": request.user,
            "offer": offer_obj,
            "address": address_obj,
        }

        try:
            UserRedeemedOffers.objects.create(**data)
            user_obj.decrease_points(offer_required_points)
            user_obj.save()
            return api_response(
                True,
                201,
                "Offer redeemed successfully. Please wait for an admin response.",
            )

        except Exception as e:
            return api_response(False, 500, ERROR_500_MSG, error=str(e))


class UserAccountDeleteView(UserMixin):
    def get(self, request):
        try:
            user_obj = UserModel.objects.get(id=request.user.id)
        except:
            return api_response(False, 404, "User does not exist")

        usr_phone = user_obj.phone_number
        usr_email = user_obj.email
        user_obj.phone_number = usr_phone + dlt_value()
        user_obj.email = usr_email + dlt_value()
        user_obj.save()
        user_obj.delete()
        OTPLog.objects.filter(Q(username=usr_phone) | Q(username=usr_email)).delete()
        return api_response(True, 200, "Account deleted successfully.")


from core.logs import Logger

contact_logger = Logger("user_contacts.log")


class UploadUserContactView(UserMixin):
    def post(self, request):
        contact_logger.info(f"Upload contacts >> {request.data}")
        return api_response(True, 200, "Contact successfully uploaded")
        # serializer = StoreUserContactSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return api_response(True, 201, data=serializer.data)
        # return api_response(False, 400, data=serializer.errors)
