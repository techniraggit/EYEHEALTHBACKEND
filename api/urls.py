from django.urls import path
from api.views.accounts import *
from api.views.user_apis import *

urlpatterns = [
    path("verification_otp", VerificationOTPView.as_view()),
    path("register", RegisterView.as_view()),
    path("send_login_otp", SendLoginOTP.as_view()),
    path("verify_login_otp", VerifyLoginOTPView.as_view()),
    path("validate_referral_code", ValidateReferralCode.as_view()),
    path("user_notification", NotificationView.as_view()),
]
