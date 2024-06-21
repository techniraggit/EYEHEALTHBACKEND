from utilities.utils import is_valid_phone, is_valid_email
from api.serializers.accounts import (
    UserSerializer,
    UserModel,
    LoginSerializer,
)
from utilities.services.sms import send_sms
from utilities.services.email import send_email
from django.template.loader import render_to_string

from rest_framework.views import APIView
from core.utils import api_response
from api.models.accounts import OTPLog
from utilities.utils import (
    generate_otp,
    verify_otp,
    get_tokens_for_user,
    phone_or_email,
)
from core.constants import SMS_TEMPLATE, ERROR_500_MSG


class IsAlreadyVerified(APIView):
    def get(self, request):
        username = request.GET.get("username")
        if not username:
            return api_response(False, 400, "username required")
        is_verified = OTPLog.objects.filter(username=username).exists()
        return api_response(True, 200, is_verified=is_verified)


class VerificationOTPView(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return api_response(False, 400, "username required")

        contact_type = phone_or_email(username)
        if contact_type == "email":
            if not is_valid_email(username):
                return api_response(False, 400, "Not a valid email address")
        else:
            if not is_valid_phone(username):
                return api_response(False, 400, "Not a valid phone number")

        OTPLog.objects.create(username=username)
        otp = generate_otp(username)

        try:
            if contact_type == "email":
                body = render_to_string("email/verify_email.html", {"otp": otp})
                send_email("Verification OTP", body, [username])
            else:
                message = SMS_TEMPLATE["send_otp"].format(otp=otp)
                send_sms(username, message)

            return api_response(True, 200, f"OTP sent successfully to {username}.")
        except Exception as e:
            return api_response(False, 500, ERROR_500_MSG, error=str(e))

    def patch(self, request):
        username = request.data.get("username")
        otp = request.data.get("otp")
        if not username or not otp:
            return api_response(False, 400, "required fields are missing")
        try:
            otp_obj = OTPLog.objects.get(username=username)
            otp_obj.is_verify = verify_otp(username, otp)
            otp_obj.save()
            if otp_obj.is_verify:
                return api_response(True, 200, "OTP verified successfully")
            else:
                return api_response(False, 400, "OTP expired, Try again later")
        except:
            return api_response(False, 404, "Username does'nt exist")


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            id = serializer.data.get("id")
            user_obj = UserModel.objects.get(id=id)
            access_token, refresh_token = get_tokens_for_user(user_obj)
            tokens = dict(access_token=access_token, refresh_token=refresh_token)
            return api_response(True, 201, data=serializer.data, tokens=tokens)
        return api_response(False, 400, data=serializer.errors)


class SendLoginOTP(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return api_response(False, 400, "username required")

        otp = generate_otp(username)
        if phone_or_email(username) == "email":
            try:
                try:
                    UserModel.objects.get(email=username)
                except:
                    return api_response(False, 404, "User does not exists")

                body = render_to_string("email/verify_email.html", {"otp": otp})
                send_email("Verification OTP", body, [username])
                return api_response(True, 200, f"OTP sent successfully to {username}.")

            except Exception as e:
                # raise e
                return api_response(False, 500, "Something went wrong")

        else:
            try:
                UserModel.objects.get(phone_number=username)
            except:
                return api_response(False, 404, "User does not exists")

            message = SMS_TEMPLATE["send_otp"].format(otp=otp)
            send_sms(username, message)
            return api_response(False, 200, f"OTP sent successfully to {username}.")


class VerifyLoginOTPView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = serializer.validated_data["tokens"]
            return api_response(
                True, 200, message="Logged In successfully", data=user, tokens=token
            )
        return api_response(False, 400, data=serializer.errors)


class ValidateReferralCode(APIView):
    def get(self, request):
        referral_code = request.GET.get("referral_code")
        if not referral_code:
            return api_response(False, 400, "Referral code required")
        is_valid = UserModel.objects.filter(referral_code=referral_code).exists()
        return api_response(True, 200, is_valid=is_valid)
