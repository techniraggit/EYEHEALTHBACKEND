from uuid import uuid4
from utilities.utils import (
    verify_otp,
    phone_or_email,
    get_tokens_for_user,
)
from rest_framework import serializers
from api.models.accounts import ( # Accounts models
    UserModel,
    OTPLog,
    DeviceInfo,
    ReferTrack,
    UserAddress,
    UserPoints,
)
from api.models.subscription import UserSubscription, SubscriptionPlan
from django.utils import timezone
from .base import BaseSerializer
from datetime import datetime, timedelta
from api.views.strip_apis import CreateCustomer
import logging

logger = logging.getLogger(__name__)


class DeviceInfoSerializer(BaseSerializer):
    class Meta:
        model = DeviceInfo
        fields = ["token", "device_type"]


class UserAddressSerializer(BaseSerializer):
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = UserAddress
        fields = [
            "address_id",
            "address",
            "postal_code",
            "city",
            "state",
            "country",
            "full_address",
            "full_name",
            "phone_number",
            "email",
            "locality",
            "is_default",
            "address_type",
        ]
        extra_kwargs = {"address_id": {"read_only": True}}

    def get_full_address(self, obj):
        return obj.get_full_address()

    def create(self, validated_data):
        user = validated_data.get("user")
        is_default = validated_data.get("is_default", False)

        if not UserAddress.objects.filter(user=user).exists():
            stripe_customer_id = CreateCustomer(
                name=user.get_full_name(),
                email=user.email,
                address=validated_data.get("address"),
                postal_code=validated_data.get("postal_code"),
                city=validated_data.get("city"),
                state=validated_data.get("state"),
                country=validated_data.get("country"),
            )
            user.stripe_customer_id = stripe_customer_id
            user.save()
            validated_data["is_default"] = True
        else:
            if is_default:
                # If setting a new default address, unset the previous default
                UserAddress.objects.filter(user=user, is_default=True).update(
                    is_default=False
                )

        address = UserAddress.objects.create(**validated_data)
        return address

    def update(self, instance, validated_data):
        is_default = validated_data.get("is_default", False)

        # Update the fields of the existing instance
        instance.address = validated_data.get("address", instance.address)
        instance.postal_code = validated_data.get("postal_code", instance.postal_code)
        instance.city = validated_data.get("city", instance.city)
        instance.state = validated_data.get("state", instance.state)
        instance.country = validated_data.get("country", instance.country)
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.email = validated_data.get("email", instance.email)
        instance.locality = validated_data.get("locality", instance.locality)
        instance.address_type = validated_data.get(
            "address_type", instance.address_type
        )

        # Handle the default address logic
        if is_default:
            UserAddress.objects.filter(user=instance.user, is_default=True).update(
                is_default=False
            )
            instance.is_default = True
        else:
            instance.is_default = validated_data.get("is_default", instance.is_default)

        instance.save()
        return instance

from api.models.rewards import GlobalPointsModel

class UserSerializer(serializers.ModelSerializer):
    device_token = DeviceInfoSerializer(many=True, read_only=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "dob",
            "image",
            "points",
            "referral_code",
            "latitude",
            "longitude",
            "device_token",
            # "addresses",
            "stripe_customer_id",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "referral_code": {"validators": []},
            "points": {"read_only": True},
            "customer_id": {"read_only": True},
        }

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        try:
            otp_log = OTPLog.objects.get(username=value)
            if not otp_log.is_verify:
                raise serializers.ValidationError("Phone number not verified.")
        except OTPLog.DoesNotExist:
            raise serializers.ValidationError("Phone number not verified.")

        return value

    def validate_email(self, value):
        try:
            otp_log = OTPLog.objects.get(username=value)
            if not otp_log.is_verify:
                raise serializers.ValidationError("Email not verified.")
        except OTPLog.DoesNotExist:
            raise serializers.ValidationError("Email not verified.")
        return value

    def validate_dob(self, value):
        today = datetime.now().date()
        if value >= today:
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        if value < today - timedelta(days=365 * 150):
            raise serializers.ValidationError(
                "Date of birth cannot be more than 150 years ago."
            )
        return value

    def validate(self, data):
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        referral_code = data.get("referral_code")
        dob = data.get("dob")

        if not dob:
            raise serializers.ValidationError("DOB required.")

        if referral_code:
            if not UserModel.objects.filter(referral_code=referral_code).exists():
                raise serializers.ValidationError(
                    "Provided 'referral code' is not valid."
                )

        if latitude is not None and longitude is None:
            raise serializers.ValidationError(
                "If latitude is provided, longitude must also be provided."
            )

        return data

    def create(self, validated_data):
        device_token_data = validated_data.pop("device_token", None)
        referral_code = validated_data.pop("referral_code", None)

        user = UserModel.objects.create(
            **validated_data, referral_code=str(uuid4()).split("-")[0]
        )

        if referral_code:
            referred_by = UserModel.objects.get(referral_code=referral_code)
            ReferTrack.objects.create(user=user, referred_by=referred_by)
            try:
                points = GlobalPointsModel.objects.get(
                    event_type="referral"
                ).value
                usr_pnt = UserPoints.objects.create(
                    user=referred_by,
                    event_type="referral",
                )
                usr_pnt.increase_points(points)
                usr_pnt.save()
            except Exception as e:
                logger.error(str(e))

        if device_token_data:
            DeviceInfo.objects.create(user=user, **device_token_data)

        plan = SubscriptionPlan.objects.get(plan_type="basic")
        end_date = timezone.now() + timezone.timedelta(days=plan.duration)
        UserSubscription.objects.create(
            user = user,
            plan = plan,
            end_date = end_date,
            is_active = True,
            payment_method = "free",
            paid_amount = 0,
            payment_status = "success"
        )

        return user


class ProfileSerializer(BaseSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "referral_code",
            "stripe_customer_id",
            "points",
            "email",
            "image",
            "age",
        ]
        extra_kwargs = {
            "points": {"read_only": True},
            "stripe_customer_id": {"read_only": True},
        }

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        try:
            if not OTPLog.objects.get(username=value).is_verify:
                raise serializers.ValidationError("Phone number not verified.")
        except:
            raise serializers.ValidationError("Phone number not verified.")

        return value

    def validate_email(self, value):
        try:
            if not OTPLog.objects.get(username=value).is_verify:
                raise serializers.ValidationError("Email not verified.")
        except:
            raise serializers.ValidationError("Email not verified.")
        return value

    def get_age(self, object):
        return object.age()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    otp = serializers.CharField(max_length=10, required=True)
    device_type = serializers.CharField(max_length=50, required=True)
    device_token = serializers.CharField(max_length=500, required=True)

    def validate(self, data):
        username = data.get("username")
        otp = data.get("otp")
        device_type = data.get("device_type")
        device_token = data.get("device_token")

        is_verified = verify_otp(username, otp)
        if not is_verified:
            raise serializers.ValidationError("OTP provided is not valid")
        if phone_or_email(username) == "phone":
            user_obj = UserModel.objects.get(phone_number=username)
        else:
            user_obj = UserModel.objects.get(email=username)
            user_obj.last_login = timezone.now()
            user_obj.save()
        access_token, refresh_token = get_tokens_for_user(user_obj)
        tokens = dict(access_token=access_token, refresh_token=refresh_token)
        DeviceInfo.objects.get_or_create(
            user=user_obj,
            token=device_token,
            device_type=device_type,
        )

        data["user"] = UserSerializer(user_obj).data
        data["tokens"] = tokens
        return data
